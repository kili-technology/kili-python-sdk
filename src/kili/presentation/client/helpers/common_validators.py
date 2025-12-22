"""Module for common argument validators across client methods."""

import warnings
from typing import Any, Optional

from kili.domain.types import ListOrTuple


def disable_tqdm_if_as_generator(
    as_generator: bool, disable_tqdm: Optional[bool]
) -> Optional[bool]:
    """Disable tqdm in user-facing queries method if the return type is asked as a generator."""
    if as_generator and not disable_tqdm:
        disable_tqdm = True
        warnings.warn(
            "tqdm has been forced disabled because its behavior is not compatible with the"
            " generator return type",
            stacklevel=2,
        )
    return disable_tqdm


def resolve_disable_tqdm(
    disable_tqdm: bool | None, client_disable_tqdm: bool | None
) -> bool | None:
    """Resolve the disable_tqdm parameter with priority: function param > client global setting.

    Args:
        disable_tqdm: The disable_tqdm parameter passed to the function.
        client_disable_tqdm: The global disable_tqdm setting from the client.
            Can be None if the client doesn't have this attribute set (e.g., in tests).

    Returns:
        The resolved disable_tqdm value, or None if both are None (to use function default).

    Examples:
        >>> resolve_disable_tqdm(True, False)  # Function param takes priority
        True
        >>> resolve_disable_tqdm(None, True)   # Use client global setting
        True
        >>> resolve_disable_tqdm(None, None)   # Use function default
        None
    """
    if disable_tqdm is not None:
        return disable_tqdm
    return client_disable_tqdm


def assert_all_arrays_have_same_size(
    arrays: list[Optional[ListOrTuple[Any]]], raise_error: bool = True
) -> bool:
    """Assert that all given arrays have the same size if they are not None."""
    sizes_arrays = {len(array) for array in arrays if array is not None}
    if len(sizes_arrays) > 1:
        if raise_error:
            raise ValueError("All arrays should have the same length")
        return False
    return True
