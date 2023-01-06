"""
Helpers for the label mutations
"""
from typing import List, Optional

from kili.exceptions import IncompatibleArgumentsError, MissingArgumentError


def check_asset_identifier_arguments(
    project_id: Optional[str],
    asset_id_array: Optional[List[str]],
    asset_external_id_array: Optional[List[str]],
):
    """
    Check that a list of assets can be identified either by their asset IDs or their external IDs
    """

    if asset_id_array is not None:
        if asset_external_id_array is not None:
            raise IncompatibleArgumentsError(
                "Either provide asset IDs or asset external IDs. Not both at the same time."
            )
        return True
    if project_id is None or asset_external_id_array is None:
        raise MissingArgumentError(
            "Either provide asset IDs or project ID with asset external IDs."
        )
    return True
