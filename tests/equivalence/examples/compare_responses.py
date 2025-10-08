"""Example script for comparing legacy and v2 responses.

This script demonstrates how to compare responses from legacy and v2
implementations to verify semantic equivalence.
"""

import json

# Add parent directory to path for imports
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from comparator import EquivalenceAssertion, ResponseComparator  # noqa: E402
from normalizer import DiffGenerator, PayloadNormalizer  # noqa: E402


def example_basic_comparison():
    """Example: Basic response comparison."""
    print("=" * 60)
    print("Example 1: Basic Response Comparison")
    print("=" * 60)

    # Legacy response (dict)
    legacy_response = {
        "id": "asset_123",
        "externalId": "image_001",
        "content": "https://example.com/image.jpg",
        "status": "TODO",
        "__typename": "Asset",  # GraphQL metadata
    }

    # V2 response (TypedDict as dict)
    v2_response = {
        "id": "asset_123",
        "externalId": "image_001",
        "content": "https://example.com/image.jpg",
        "status": "TODO",
    }

    # Compare
    comparator = ResponseComparator()
    result = comparator.compare(legacy_response, v2_response)

    print(f"\nLegacy: {json.dumps(legacy_response, indent=2)}")
    print(f"\nV2: {json.dumps(v2_response, indent=2)}")
    print(f"\nEquivalent: {result.is_equivalent}")

    if result.is_equivalent:
        print("✓ Responses are equivalent!")
    else:
        print("✗ Responses differ:")
        for diff in result.differences:
            print(f"  - {diff}")


def example_list_comparison():
    """Example: List response comparison with sorting."""
    print("\n" + "=" * 60)
    print("Example 2: List Response Comparison")
    print("=" * 60)

    # Legacy response (unordered)
    legacy_response = [
        {"id": "2", "name": "Asset B"},
        {"id": "1", "name": "Asset A"},
        {"id": "3", "name": "Asset C"},
    ]

    # V2 response (different order)
    v2_response = [
        {"id": "1", "name": "Asset A"},
        {"id": "3", "name": "Asset C"},
        {"id": "2", "name": "Asset B"},
    ]

    # Compare
    comparator = ResponseComparator()
    result = comparator.compare(legacy_response, v2_response)

    print(f"\nLegacy order: {[a['id'] for a in legacy_response]}")
    print(f"V2 order: {[a['id'] for a in v2_response]}")
    print(f"\nEquivalent: {result.is_equivalent}")

    if result.is_equivalent:
        print("✓ Lists are equivalent (after normalization)!")


def example_nested_comparison():
    """Example: Nested object comparison."""
    print("\n" + "=" * 60)
    print("Example 3: Nested Object Comparison")
    print("=" * 60)

    # Legacy response
    legacy_response = {
        "id": "asset_123",
        "labels": [
            {
                "id": "label_1",
                "author": {
                    "id": "user_1",
                    "email": "user@example.com",
                    "__typename": "User",
                },
            }
        ],
    }

    # V2 response
    v2_response = {
        "id": "asset_123",
        "labels": [
            {
                "id": "label_1",
                "author": {
                    "id": "user_1",
                    "email": "user@example.com",
                },
            }
        ],
    }

    # Compare
    comparator = ResponseComparator()
    result = comparator.compare(legacy_response, v2_response)

    print(f"\nEquivalent: {result.is_equivalent}")

    if result.is_equivalent:
        print("✓ Nested structures are equivalent!")


def example_difference_detection():
    """Example: Detecting and displaying differences."""
    print("\n" + "=" * 60)
    print("Example 4: Difference Detection")
    print("=" * 60)

    # Legacy response
    legacy_response = {
        "id": "asset_123",
        "status": "TODO",
        "metadata": {"camera": "drone", "altitude": 100},
    }

    # V2 response (different metadata)
    v2_response = {
        "id": "asset_123",
        "status": "LABELED",  # Different status
        "metadata": {"camera": "drone", "altitude": 150},  # Different altitude
    }

    # Compare
    comparator = ResponseComparator()
    result = comparator.compare(legacy_response, v2_response)

    print(f"\nEquivalent: {result.is_equivalent}")

    if not result.is_equivalent:
        print("\nDifferences found:")
        for diff in result.differences:
            print(f"  - {diff}")


def example_count_comparison():
    """Example: Comparing count responses."""
    print("\n" + "=" * 60)
    print("Example 5: Count Response Comparison")
    print("=" * 60)

    from comparator import create_count_comparator

    # Legacy response
    legacy_count = 42

    # V2 response
    v2_count = 42

    # Use count comparator
    count_comparator = create_count_comparator()
    result = count_comparator(legacy_count, v2_count)

    print(f"\nLegacy count: {legacy_count}")
    print(f"V2 count: {v2_count}")
    print(f"Equivalent: {result.is_equivalent}")

    if result.is_equivalent:
        print("✓ Counts match!")


def example_assertion():
    """Example: Using assertions in tests."""
    print("\n" + "=" * 60)
    print("Example 6: Using Equivalence Assertions")
    print("=" * 60)

    legacy_response = {"id": "123", "name": "test"}
    v2_response = {"id": "123", "name": "test"}

    comparator = ResponseComparator()
    result = comparator.compare(legacy_response, v2_response)

    try:
        EquivalenceAssertion.assert_equivalent(result, message="Asset responses must be equivalent")
        print("\n✓ Assertion passed!")
    except AssertionError as e:
        print(f"\n✗ Assertion failed: {e}")


def example_manual_normalization():
    """Example: Manual normalization and diff generation."""
    print("\n" + "=" * 60)
    print("Example 7: Manual Normalization")
    print("=" * 60)

    legacy = {
        "id": "123",
        "items": [{"id": "2"}, {"id": "1"}],
        "__typename": "Response",
    }

    v2 = {
        "id": "123",
        "items": [{"id": "1"}, {"id": "2"}],
    }

    # Normalize
    normalizer = PayloadNormalizer()
    norm_legacy, norm_v2 = normalizer.normalize_for_comparison(legacy, v2)

    print("\nOriginal legacy:")
    print(json.dumps(legacy, indent=2))
    print("\nNormalized legacy:")
    print(json.dumps(norm_legacy, indent=2))

    print(f"\nEquivalent after normalization: {norm_legacy == norm_v2}")

    if norm_legacy != norm_v2:
        # Generate diff
        diff_gen = DiffGenerator()
        diffs = diff_gen.generate_diff(norm_legacy, norm_v2)
        print("\nDifferences:")
        for diff in diffs:
            print(f"  - {diff}")


def main():
    """Run all examples."""
    print("\nEquivalence Testing Examples")
    print("=" * 60)

    example_basic_comparison()
    example_list_comparison()
    example_nested_comparison()
    example_difference_detection()
    example_count_comparison()
    example_assertion()
    example_manual_normalization()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
