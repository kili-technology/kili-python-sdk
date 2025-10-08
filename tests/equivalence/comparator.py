"""Response comparison utilities for equivalence testing.

This module provides sophisticated comparison capabilities to verify
semantic equivalence between legacy and v2 API responses.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .normalizer import DiffGenerator, PayloadNormalizer


class ComparisonStatus(Enum):
    """Status of a comparison."""

    EQUIVALENT = "equivalent"
    DIFFERENT = "different"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class ComparisonResult:
    """Result of comparing legacy and v2 responses."""

    status: ComparisonStatus
    legacy_response: Any
    v2_response: Any
    differences: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_equivalent(self) -> bool:
        """Check if responses are equivalent."""
        return self.status == ComparisonStatus.EQUIVALENT

    @property
    def has_differences(self) -> bool:
        """Check if responses have differences."""
        return len(self.differences) > 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status": self.status.value,
            "legacy_response": self.legacy_response,
            "v2_response": self.v2_response,
            "differences": self.differences,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }


class ResponseComparator:
    """Compare responses from legacy and v2 implementations.

    This class provides sophisticated comparison logic that goes beyond
    simple equality to check semantic equivalence.
    """

    def __init__(
        self,
        normalizer: Optional[PayloadNormalizer] = None,
        diff_generator: Optional[DiffGenerator] = None,
        custom_comparators: Optional[Dict[str, Callable]] = None,
    ):
        """Initialize the comparator.

        Args:
            normalizer: Payload normalizer to use (default: PayloadNormalizer)
            diff_generator: Diff generator to use (default: DiffGenerator)
            custom_comparators: Custom comparison functions by method name
        """
        self.normalizer = normalizer or PayloadNormalizer()
        self.diff_generator = diff_generator or DiffGenerator()
        self.custom_comparators = custom_comparators or {}

    def compare(
        self,
        legacy_response: Any,
        v2_response: Any,
        method_name: Optional[str] = None,
        strict: bool = False,
    ) -> ComparisonResult:
        """Compare legacy and v2 responses.

        Args:
            legacy_response: Response from legacy implementation
            v2_response: Response from v2 implementation
            method_name: Name of the method (for custom comparison)
            strict: Whether to use strict comparison (no normalization)

        Returns:
            ComparisonResult with details
        """
        # Check for custom comparator
        if method_name and method_name in self.custom_comparators:
            return self.custom_comparators[method_name](legacy_response, v2_response)

        try:
            # Normalize responses if not strict
            if not strict:
                legacy_norm, v2_norm = self.normalizer.normalize_for_comparison(
                    legacy_response, v2_response
                )
            else:
                legacy_norm, v2_norm = legacy_response, v2_response

            # Compare
            if legacy_norm == v2_norm:
                return ComparisonResult(
                    status=ComparisonStatus.EQUIVALENT,
                    legacy_response=legacy_response,
                    v2_response=v2_response,
                    metadata={"normalized": not strict},
                )

            # Generate differences
            differences = self.diff_generator.generate_diff(legacy_norm, v2_norm)

            return ComparisonResult(
                status=ComparisonStatus.DIFFERENT,
                legacy_response=legacy_response,
                v2_response=v2_response,
                differences=differences,
                metadata={"normalized": not strict},
            )

        except Exception as e:  # pylint: disable=broad-except
            return ComparisonResult(
                status=ComparisonStatus.ERROR,
                legacy_response=legacy_response,
                v2_response=v2_response,
                error_message=str(e),
            )

    def compare_batch(
        self,
        pairs: List[tuple[Any, Any]],
        method_name: Optional[str] = None,
        strict: bool = False,
    ) -> List[ComparisonResult]:
        """Compare multiple pairs of responses.

        Args:
            pairs: List of (legacy_response, v2_response) tuples
            method_name: Name of the method
            strict: Whether to use strict comparison

        Returns:
            List of ComparisonResults
        """
        return [self.compare(legacy, v2, method_name, strict) for legacy, v2 in pairs]

    def register_custom_comparator(
        self,
        method_name: str,
        comparator: Callable[[Any, Any], ComparisonResult],
    ) -> None:
        """Register a custom comparison function for a method.

        Args:
            method_name: Name of the method
            comparator: Function that takes (legacy, v2) and returns ComparisonResult
        """
        self.custom_comparators[method_name] = comparator


class EquivalenceAssertion:
    """Assertion utilities for equivalence testing."""

    @staticmethod
    def assert_equivalent(
        result: ComparisonResult,
        message: Optional[str] = None,
    ) -> None:
        """Assert that responses are equivalent.

        Args:
            result: Comparison result to check
            message: Optional custom message

        Raises:
            AssertionError: If responses are not equivalent
        """
        if result.status == ComparisonStatus.ERROR:
            raise AssertionError(f"{message or 'Comparison failed'}: {result.error_message}")

        if not result.is_equivalent:
            diff_str = "\n".join(result.differences)
            raise AssertionError(f"{message or 'Responses not equivalent'}:\n{diff_str}")

    @staticmethod
    def assert_batch_equivalent(
        results: List[ComparisonResult],
        message: Optional[str] = None,
    ) -> None:
        """Assert that all batch comparisons are equivalent.

        Args:
            results: List of comparison results
            message: Optional custom message

        Raises:
            AssertionError: If any comparison is not equivalent
        """
        failed = [r for r in results if not r.is_equivalent]

        if failed:
            errors = [f"Result {i}: {r.differences}" for i, r in enumerate(failed)]
            raise AssertionError(
                f"{message or 'Batch comparison failed'} "
                f"({len(failed)}/{len(results)} failed):\n" + "\n".join(errors)
            )


# Example custom comparators


def create_pagination_comparator() -> Callable[[Any, Any], ComparisonResult]:
    """Create a custom comparator for paginated responses.

    Paginated responses may differ in structure but should contain
    the same data when all pages are aggregated.
    """

    def compare_paginated(legacy: Any, v2: Any) -> ComparisonResult:
        """Compare paginated responses."""
        # This is a simplified example - real implementation would
        # aggregate pages and compare the full dataset
        try:
            # Assume both are generators/lists of items
            legacy_items = list(legacy) if hasattr(legacy, "__iter__") else [legacy]
            v2_items = list(v2) if hasattr(v2, "__iter__") else [v2]

            if len(legacy_items) != len(v2_items):
                return ComparisonResult(
                    status=ComparisonStatus.DIFFERENT,
                    legacy_response=legacy,
                    v2_response=v2,
                    differences=[
                        f"Item count mismatch: legacy={len(legacy_items)}, v2={len(v2_items)}"
                    ],
                )

            # Sort by ID for comparison
            legacy_sorted = sorted(
                legacy_items, key=lambda x: x.get("id", "") if isinstance(x, dict) else str(x)
            )
            v2_sorted = sorted(
                v2_items, key=lambda x: x.get("id", "") if isinstance(x, dict) else str(x)
            )

            # Use standard comparison
            comparator = ResponseComparator()
            return comparator.compare(legacy_sorted, v2_sorted)

        except Exception as e:  # pylint: disable=broad-except
            return ComparisonResult(
                status=ComparisonStatus.ERROR,
                legacy_response=legacy,
                v2_response=v2,
                error_message=f"Pagination comparison error: {e}",
            )

    return compare_paginated


def create_count_comparator() -> Callable[[Any, Any], ComparisonResult]:
    """Create a custom comparator for count methods.

    Count methods should return the same integer value.
    """

    def compare_counts(legacy: Any, v2: Any) -> ComparisonResult:
        """Compare count responses."""
        try:
            legacy_count = int(legacy)
            v2_count = int(v2)

            if legacy_count == v2_count:
                return ComparisonResult(
                    status=ComparisonStatus.EQUIVALENT,
                    legacy_response=legacy,
                    v2_response=v2,
                )

            return ComparisonResult(
                status=ComparisonStatus.DIFFERENT,
                legacy_response=legacy,
                v2_response=v2,
                differences=[f"Count mismatch: legacy={legacy_count}, v2={v2_count}"],
            )

        except (TypeError, ValueError) as e:
            return ComparisonResult(
                status=ComparisonStatus.ERROR,
                legacy_response=legacy,
                v2_response=v2,
                error_message=f"Invalid count value: {e}",
            )

    return compare_counts
