"""Tests for check_asset_workflow_arguments in domain/asset/helpers.py."""

import pytest

from kili.domain.asset.helpers import check_asset_workflow_arguments


class TestCheckAssetWorkflowArgumentsGroupName:
    """Tests for group_name validation in check_asset_workflow_arguments."""

    def test_group_name_raises_on_v1_project(self):
        """group_name must be rejected on WorkflowV1 projects."""
        with pytest.raises(ValueError, match="group_name"):
            check_asset_workflow_arguments(
                project_workflow_version="V1",
                asset_workflow_filters={"group_name": ["GroupA"]},
            )

    def test_group_name_is_accepted_on_v2_project(self):
        """group_name must be silently accepted on WorkflowV2 projects."""
        # Should not raise
        check_asset_workflow_arguments(
            project_workflow_version="V2",
            asset_workflow_filters={"group_name": ["GroupA"]},
        )

    def test_group_name_none_does_not_raise_on_v1(self):
        """None group_name must not trigger a rejection on V1 projects."""
        # Should not raise
        check_asset_workflow_arguments(
            project_workflow_version="V1",
            asset_workflow_filters={"group_name": None},
        )

    def test_group_name_combined_with_step_status_on_v2(self):
        """group_name combined with step_status_in on V2 must not raise."""
        # Should not raise
        check_asset_workflow_arguments(
            project_workflow_version="V2",
            asset_workflow_filters={
                "group_name": ["GroupA"],
                "step_status_in": ["TO_DO"],
            },
        )
