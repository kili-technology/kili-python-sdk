"""Module for common argument validators across client methods."""

import warnings
from typing import Any, List, Optional

from kili.domain.types import ListOrTuple
from kili.exceptions import IncompatibleArgumentsError, MissingArgumentError


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


def check_asset_identifier_arguments(
    project_id: Optional[str],
    asset_id_array: Optional[List[str]],
    asset_external_id_array: Optional[List[str]],
) -> None:
    # pylint: disable=line-too-long
    """Check that a list of assets can be identified either by their asset IDs or their external IDs."""
    if asset_id_array is not None:
        if asset_external_id_array is not None:
            raise IncompatibleArgumentsError(
                "Either provide asset IDs or asset external IDs. Not both at the same time."
            )
        return

    if project_id is None or asset_external_id_array is None:
        raise MissingArgumentError(
            "Either provide asset IDs or project ID with asset external IDs."
        )
