"""Module for common argument validators across client methods."""

import warnings
from typing import Any, List, Optional

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


def assert_all_arrays_have_same_size(
    arrays: List[Optional[ListOrTuple[Any]]], raise_error: bool = True
) -> bool:
    """Assert that all given arrays have the same size if they are not None."""
    sizes_arrays = {len(array) for array in arrays if array is not None}
    if len(sizes_arrays) > 1:
        if raise_error:
            raise ValueError("All arrays should have the same length")
        return False
    return True
