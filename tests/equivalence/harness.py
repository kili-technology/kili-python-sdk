"""Test harness for automated equivalence testing.

This module provides the main test harness that orchestrates recording,
replaying, and comparing legacy vs v2 API implementations.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Protocol

from .comparator import (
    ComparisonResult,
    ComparisonStatus,
    ResponseComparator,
    create_count_comparator,
    create_pagination_comparator,
)
from .recorder import RecordedRequest, RequestRecorder


class LegacyClient(Protocol):
    """Protocol for legacy Kili client."""

    def __getattr__(self, name: str) -> Callable:
        """Get method by name."""
        ...


class V2Client(Protocol):
    """Protocol for v2 Kili client."""

    def __getattr__(self, name: str) -> Callable:
        """Get namespace/method by name."""
        ...


@dataclass
class TestCase:
    """A single equivalence test case."""

    name: str
    method_name: str
    legacy_method_path: str  # e.g., "count_assets"
    v2_method_path: str  # e.g., "assets.count"
    args: tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    skip: bool = False
    skip_reason: str = ""


@dataclass
class TestResult:
    """Result of running a test case."""

    test_case: TestCase
    comparison_result: Optional[ComparisonResult] = None
    error: Optional[str] = None
    skipped: bool = False

    @property
    def passed(self) -> bool:
        """Check if test passed."""
        if self.skipped or self.error:
            return False
        return self.comparison_result is not None and self.comparison_result.is_equivalent

    @property
    def failed(self) -> bool:
        """Check if test failed."""
        return not self.passed and not self.skipped


class EquivalenceTestHarness:
    """Main test harness for equivalence testing.

    This class orchestrates the recording, replay, and comparison of
    legacy and v2 implementations.
    """

    def __init__(
        self,
        legacy_client: Optional[Any] = None,
        v2_client: Optional[Any] = None,
        recorder: Optional[RequestRecorder] = None,
        comparator: Optional[ResponseComparator] = None,
    ):
        """Initialize the test harness.

        Args:
            legacy_client: Instance of legacy Kili client
            v2_client: Instance of v2 Kili client
            recorder: Request recorder
            comparator: Response comparator
        """
        self.legacy_client = legacy_client
        self.v2_client = v2_client
        self.recorder = recorder or RequestRecorder()
        self.comparator = comparator or ResponseComparator()

        # Register common custom comparators
        self._register_default_comparators()

    def _register_default_comparators(self) -> None:
        """Register default custom comparators for common patterns."""
        # Count methods
        count_comparator = create_count_comparator()
        self.comparator.register_custom_comparator("count_assets", count_comparator)
        self.comparator.register_custom_comparator("count_labels", count_comparator)
        self.comparator.register_custom_comparator("count_projects", count_comparator)

        # Pagination methods
        pagination_comparator = create_pagination_comparator()
        self.comparator.register_custom_comparator("assets", pagination_comparator)
        self.comparator.register_custom_comparator("labels", pagination_comparator)
        self.comparator.register_custom_comparator("projects", pagination_comparator)

    def record_legacy_request(
        self,
        method_name: str,
        args: tuple = (),
        kwargs: Optional[Dict[str, Any]] = None,
    ) -> RecordedRequest:
        """Record a request from legacy client.

        Args:
            method_name: Name of the method to call
            args: Positional arguments
            kwargs: Keyword arguments

        Returns:
            Recorded request object
        """
        kwargs = kwargs or {}

        # Get the method from legacy client
        method = self._get_method(self.legacy_client, method_name)

        # Execute and record
        try:
            response = method(*args, **kwargs)
            exception = None
        except Exception as e:  # pylint: disable=broad-except
            response = None
            exception = e

        # Extract context
        context = {}
        if "project_id" in kwargs:
            context["project_id"] = kwargs["project_id"]
        if "asset_id" in kwargs:
            context["asset_id"] = kwargs["asset_id"]
        if "label_id" in kwargs:
            context["label_id"] = kwargs["label_id"]

        return self.recorder.record(
            method_name=method_name,
            args=args,
            kwargs=kwargs,
            response=response,
            exception=exception,
            context=context,
        )

    def replay_against_v2(
        self,
        recording: RecordedRequest,
        v2_method_path: str,
    ) -> tuple[Any, Optional[Exception]]:
        """Replay a recorded request against v2 implementation.

        Args:
            recording: The recorded request to replay
            v2_method_path: Path to v2 method (e.g., "assets.count")

        Returns:
            Tuple of (response, exception)
        """
        # Get the v2 method
        method = self._get_method(self.v2_client, v2_method_path)

        # Execute
        try:
            response = method(*recording.args, **recording.kwargs)
            return response, None
        except Exception as e:  # pylint: disable=broad-except
            return None, e

    def run_test_case(self, test_case: TestCase) -> TestResult:
        """Run a single test case.

        Args:
            test_case: The test case to run

        Returns:
            Test result
        """
        if test_case.skip:
            return TestResult(
                test_case=test_case,
                skipped=True,
            )

        try:
            # Execute legacy method
            legacy_method = self._get_method(self.legacy_client, test_case.legacy_method_path)
            legacy_response = legacy_method(*test_case.args, **test_case.kwargs)
            legacy_exception = None
        except Exception as e:  # pylint: disable=broad-except
            legacy_response = None
            legacy_exception = e

        try:
            # Execute v2 method
            v2_method = self._get_method(self.v2_client, test_case.v2_method_path)
            v2_response = v2_method(*test_case.args, **test_case.kwargs)
            v2_exception = None
        except Exception as e:  # pylint: disable=broad-except
            v2_response = None
            v2_exception = e

        # Handle exception cases
        if legacy_exception or v2_exception:
            if legacy_exception and v2_exception:
                # Both raised exceptions - compare exception types
                if isinstance(legacy_exception, type(v2_exception)):
                    comparison_result = ComparisonResult(
                        status=ComparisonStatus.EQUIVALENT,
                        legacy_response=str(legacy_exception),
                        v2_response=str(v2_exception),
                        metadata={"both_raised_exception": True},
                    )
                else:
                    comparison_result = ComparisonResult(
                        status=ComparisonStatus.DIFFERENT,
                        legacy_response=str(legacy_exception),
                        v2_response=str(v2_exception),
                        differences=[
                            f"Exception type mismatch: "
                            f"legacy={type(legacy_exception).__name__}, "
                            f"v2={type(v2_exception).__name__}"
                        ],
                    )
            else:
                # Only one raised exception
                comparison_result = ComparisonResult(
                    status=ComparisonStatus.DIFFERENT,
                    legacy_response=str(legacy_exception) if legacy_exception else legacy_response,
                    v2_response=str(v2_exception) if v2_exception else v2_response,
                    differences=[
                        f"Exception mismatch: legacy_exception={legacy_exception is not None}, "
                        f"v2_exception={v2_exception is not None}"
                    ],
                )
        else:
            # Compare responses
            comparison_result = self.comparator.compare(
                legacy_response, v2_response, test_case.method_name
            )

        return TestResult(
            test_case=test_case,
            comparison_result=comparison_result,
        )

    def run_test_suite(self, test_cases: List[TestCase]) -> List[TestResult]:
        """Run a suite of test cases.

        Args:
            test_cases: List of test cases to run

        Returns:
            List of test results
        """
        return [self.run_test_case(tc) for tc in test_cases]

    def _get_method(self, client: Any, method_path: str) -> Callable:
        """Get a method from a client by path.

        Args:
            client: The client object
            method_path: Dot-separated path to method (e.g., "assets.count")

        Returns:
            The method callable

        Raises:
            AttributeError: If method not found
        """
        parts = method_path.split(".")
        obj = client

        for part in parts:
            obj = getattr(obj, part)

        if not callable(obj):
            raise AttributeError(f"'{method_path}' is not callable")

        return obj


@dataclass
class TestSuiteReport:
    """Report of test suite execution."""

    total: int
    passed: int
    failed: int
    skipped: int
    results: List[TestResult]

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total == 0:
            return 0.0
        return (self.passed / (self.total - self.skipped)) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "skipped": self.skipped,
            "success_rate": f"{self.success_rate:.2f}%",
            "results": [
                {
                    "name": r.test_case.name,
                    "passed": r.passed,
                    "failed": r.failed,
                    "skipped": r.skipped,
                    "differences": (r.comparison_result.differences if r.comparison_result else []),
                }
                for r in self.results
            ],
        }


def generate_report(results: List[TestResult]) -> TestSuiteReport:
    """Generate a test suite report.

    Args:
        results: List of test results

    Returns:
        Test suite report
    """
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if r.failed)
    skipped = sum(1 for r in results if r.skipped)

    return TestSuiteReport(
        total=total,
        passed=passed,
        failed=failed,
        skipped=skipped,
        results=results,
    )
