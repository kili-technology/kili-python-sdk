"""Equivalence tests for Asset methods.

This module tests semantic equivalence between legacy and v2 asset methods.
"""

import pytest

from kili.client import Kili
from tests.equivalence.comparator import EquivalenceAssertion
from tests.equivalence.fixtures import ASSET_TEST_CASES
from tests.equivalence.harness import EquivalenceTestHarness, generate_report


@pytest.fixture()
def legacy_client(mocker):
    """Create a mocked legacy Kili client."""
    # In real tests, this would be a real client or a comprehensive mock
    mock_client = mocker.MagicMock(spec=Kili)

    # Mock count_assets
    mock_client.count_assets.return_value = 42

    # Mock assets (returns list)
    mock_client.assets.return_value = [
        {
            "id": "asset1",
            "externalId": "ext1",
            "content": "http://example.com/image1.jpg",
            "status": "TODO",
        },
        {
            "id": "asset2",
            "externalId": "ext2",
            "content": "http://example.com/image2.jpg",
            "status": "LABELED",
        },
    ]

    return mock_client


@pytest.fixture()
def v2_client(mocker):
    """Create a mocked v2 Kili client."""
    # In real tests, this would use the actual v2 implementation
    mock_client = mocker.MagicMock()

    # Mock assets namespace
    mock_assets = mocker.MagicMock()
    mock_assets.count.return_value = 42
    mock_assets.list.return_value = [
        {
            "id": "asset1",
            "externalId": "ext1",
            "content": "http://example.com/image1.jpg",
            "status": "TODO",
        },
        {
            "id": "asset2",
            "externalId": "ext2",
            "content": "http://example.com/image2.jpg",
            "status": "LABELED",
        },
    ]
    mock_client.assets = mock_assets

    return mock_client


@pytest.fixture()
def test_harness(legacy_client, v2_client):  # pylint: disable=redefined-outer-name
    """Create test harness with clients."""
    return EquivalenceTestHarness(
        legacy_client=legacy_client,
        v2_client=v2_client,
    )


class TestAssetEquivalence:
    """Test equivalence of asset methods."""

    def test_count_assets_basic(self, test_harness):  # pylint: disable=redefined-outer-name
        """Test count_assets returns same value as assets.count."""
        test_case = next(tc for tc in ASSET_TEST_CASES if tc.name == "count_assets_basic")
        result = test_harness.run_test_case(test_case)

        diffs = (
            result.comparison_result.differences if result.comparison_result else "No comparison"
        )
        assert result.passed, f"Test failed: {diffs}"

    def test_assets_list_basic(self, test_harness):  # pylint: disable=redefined-outer-name
        """Test assets returns same data as assets.list."""
        test_case = next(tc for tc in ASSET_TEST_CASES if tc.name == "assets_list_basic")
        result = test_harness.run_test_case(test_case)

        diffs = (
            result.comparison_result.differences if result.comparison_result else "No comparison"
        )
        assert result.passed, f"Test failed: {diffs}"

    @pytest.mark.parametrize("test_case", ASSET_TEST_CASES, ids=lambda tc: tc.name)
    def test_all_asset_methods(self, test_harness, test_case):  # pylint: disable=redefined-outer-name
        """Parametrized test for all asset methods."""
        if test_case.skip:
            pytest.skip(test_case.skip_reason)

        result = test_harness.run_test_case(test_case)

        if result.comparison_result:
            EquivalenceAssertion.assert_equivalent(
                result.comparison_result,
                message=f"Asset equivalence test failed: {test_case.name}",
            )


def test_asset_suite_report(test_harness):  # pylint: disable=redefined-outer-name
    """Test generating a report for the full asset test suite."""
    results = test_harness.run_test_suite(ASSET_TEST_CASES)
    report = generate_report(results)

    # Print report for debugging
    print("\nAsset Equivalence Test Report:")
    print(f"  Total: {report.total}")
    print(f"  Passed: {report.passed}")
    print(f"  Failed: {report.failed}")
    print(f"  Skipped: {report.skipped}")
    print(f"  Success Rate: {report.success_rate:.2f}%")

    # Assert overall success
    assert report.failed == 0, f"{report.failed} tests failed"
