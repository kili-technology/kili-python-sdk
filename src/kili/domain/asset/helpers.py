"""Helpers for the asset domain."""

import warnings
from typing import Optional

from kili.domain.asset import AssetExternalId, AssetId
from kili.domain.asset.asset import AssetWorkflowFilters
from kili.domain.project import ProjectId, WorkflowVersion
from kili.domain.types import ListOrTuple
from kili.exceptions import IncompatibleArgumentsError, MissingArgumentError


def check_asset_identifier_arguments(
    project_id: Optional[ProjectId],
    asset_id_array: Optional[ListOrTuple[AssetId]],
    asset_external_id_array: Optional[ListOrTuple[AssetExternalId]],
) -> None:
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


def check_asset_workflow_arguments(
    project_workflow_version: WorkflowVersion, asset_workflow_filters: AssetWorkflowFilters
) -> None:
    """Check asset workflow parameters relative to the project workflow version."""
    step_name_in = asset_workflow_filters.get("step_name_in")
    step_status_in = asset_workflow_filters.get("step_status_in")
    status_in = asset_workflow_filters.get("status_in")
    skipped = asset_workflow_filters.get("skipped")

    if project_workflow_version == "V2":
        if step_status_in is not None and status_in is not None:
            raise ValueError(
                "Filters step_status_in and status_in both given : only use filter step_status_in for this project."
            )
        if step_name_in is not None and status_in is not None:
            raise ValueError(
                "Filters step_name_in and status_in both given : use filter step_status_in instead of status_in for this project."  # pylint: disable=line-too-long
            )
        if status_in is not None:
            warnings.warn(
                "Filter status_in given : use filters step_status_in and step_name_in instead for this project.",
                stacklevel=1,
            )
        if skipped is not None:
            warnings.warn(
                "Filter skipped given : only use filter step_status_in with the SKIPPED step status instead for this project",  # pylint: disable=line-too-long
                stacklevel=1,
            )
        return

    # project workflow v1
    if step_name_in is not None or step_status_in is not None:
        raise ValueError(
            "Filters step_name_in and/or step_status_in given : use filter status_in for this project."
        )
