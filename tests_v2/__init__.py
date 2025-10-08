"""Integration test utilities for domain_v2 View objects.

This module provides shared utilities and helper functions for testing
the domain_v2 View objects (AssetView, LabelView, ProjectView, UserView)
against the real Kili API.

The View objects wrap dictionaries returned from the Kili API and provide
ergonomic property access while maintaining backward compatibility with
dictionary representations.

Test Configuration:
    API_KEY:
    ENDPOINT: http://localhost:4001/api/label/v2/graphql

Example:
    >>> from tests_v2 import assert_is_view, assert_view_has_dict_compatibility
    >>> from kili.domain_v2.asset import AssetView
    >>>
    >>> # Test that object is a View instance
    >>> assert_is_view(obj, AssetView)
    >>>
    >>> # Test View dictionary compatibility
    >>> assert_view_has_dict_compatibility(asset_view)
"""

from typing import Any, Type


def assert_is_view(obj: Any, view_class: Type) -> None:
    """Assert that an object is an instance of a specific View class.

    This function verifies that:
    - The object is an instance of the expected View class
    - The object has the required _data attribute
    - The object has the to_dict() method

    Args:
        obj: The object to check
        view_class: The expected View class (e.g., AssetView, LabelView)

    Raises:
        AssertionError: If the object is not a valid View instance

    Example:
        >>> from kili.domain_v2.asset import AssetView
        >>> assert_is_view(asset_obj, AssetView)
    """
    assert isinstance(
        obj, view_class
    ), f"Expected instance of {view_class.__name__}, got {type(obj).__name__}"

    # Verify View has required structure
    assert hasattr(obj, "_data"), f"{view_class.__name__} instance missing _data attribute"
    assert hasattr(obj, "to_dict"), f"{view_class.__name__} instance missing to_dict() method"

    # Verify _data is a dictionary
    assert isinstance(
        obj._data,
        dict,  # pylint: disable=protected-access
    ), f"{view_class.__name__}._data should be a dictionary"


def assert_view_has_dict_compatibility(view: Any) -> None:
    """Assert that a View object maintains dictionary compatibility.

    This function verifies that:
    - The View has a to_dict() method
    - The to_dict() method returns a dictionary
    - The returned dictionary is the same as the internal _data

    Args:
        view: The View object to check

    Raises:
        AssertionError: If the View doesn't have proper dictionary compatibility

    Example:
        >>> assert_view_has_dict_compatibility(asset_view)
    """
    # Verify to_dict() exists and returns a dictionary
    assert hasattr(view, "to_dict"), "View object missing to_dict() method"

    dict_repr = view.to_dict()
    assert isinstance(dict_repr, dict), f"to_dict() should return a dict, got {type(dict_repr)}"

    # Verify to_dict() returns the same reference as _data (zero-copy)
    assert hasattr(view, "_data"), "View object missing _data attribute"
    assert (
        dict_repr is view._data  # pylint: disable=protected-access
    ), "to_dict() should return the same reference as _data (not a copy)"


def assert_view_property_access(view: Any, property_name: str, expected_value: Any = None) -> None:
    """Assert that a View property is accessible and optionally matches an expected value.

    Args:
        view: The View object to check
        property_name: Name of the property to access
        expected_value: Optional expected value for the property

    Raises:
        AssertionError: If the property is not accessible or doesn't match expected value

    Example:
        >>> assert_view_property_access(asset_view, "id")
        >>> assert_view_property_access(asset_view, "external_id", "asset-1")
    """
    assert hasattr(view, property_name), f"View object missing property '{property_name}'"

    # Try to access the property
    try:
        actual_value = getattr(view, property_name)
    except Exception as exc:  # pylint: disable=broad-except
        raise AssertionError(f"Error accessing property '{property_name}': {exc}") from exc

    # If expected value provided, verify it matches
    if expected_value is not None:
        assert actual_value == expected_value, (
            f"Property '{property_name}' has value {actual_value!r}, "
            f"expected {expected_value!r}"
        )
