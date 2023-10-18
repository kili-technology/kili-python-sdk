"""Helpers for the asset domain."""

from typing import Optional

from kili.domain.asset import AssetExternalId, AssetId
from kili.domain.project import ProjectId
from kili.domain.types import ListOrTuple
from kili.exceptions import IncompatibleArgumentsError, MissingArgumentError


def check_asset_identifier_arguments(
    project_id: Optional[ProjectId],
    asset_id_array: Optional[ListOrTuple[AssetId]],
    asset_external_id_array: Optional[ListOrTuple[AssetExternalId]],
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
