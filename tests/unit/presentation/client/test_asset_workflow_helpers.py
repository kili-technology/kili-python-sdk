"""Tests for check_asset_workflow_arguments in domain/asset/helpers.py."""

import pytest

from kili.domain.asset.helpers import check_asset_workflow_arguments


class TestCheckAssetWorkflowArgumentsGroupName:
    """Tests for group_name_in validation in check_asset_workflow_arguments."""

    def test_group_name_in_raises_on_v1_project(self):
        """group_name_in must be rejected on WorkflowV1 projects."""
        with pytest.raises(ValueError, match="group_name_in"):
            check_asset_workflow_arguments(
                project_workflow_version="V1",
                asset_workflow_filters={"group_name_in": ["GroupA"]},
            )

    def test_group_name_in_raises_on_v2_project(self):
        """group_name_in must be rejected on WorkflowV2 projects (V3-only filter)."""
        with pytest.raises(ValueError, match="group_name_in"):
            check_asset_workflow_arguments(
                project_workflow_version="V2",
                asset_workflow_filters={"group_name_in": ["GroupA"]},
            )

    def test_group_name_in_is_accepted_on_v3_project(self):
        """group_name_in must be silently accepted on WorkflowV3 projects."""
        # Should not raise
        check_asset_workflow_arguments(
            project_workflow_version="V3",
            asset_workflow_filters={"group_name_in": ["GroupA"]},
        )

    def test_group_name_in_none_does_not_raise_on_v1(self):
        """None group_name_in must not trigger a rejection on V1 projects."""
        # Should not raise
        check_asset_workflow_arguments(
            project_workflow_version="V1",
            asset_workflow_filters={"group_name_in": None},
        )

    def test_group_name_in_combined_with_step_status_on_v3(self):
        """group_name_in combined with step_status_in on V3 must not raise."""
        # Should not raise
        check_asset_workflow_arguments(
            project_workflow_version="V3",
            asset_workflow_filters={
                "group_name_in": ["GroupA"],
                "step_status_in": ["TO_DO"],
            },
        )

    def test_group_name_not_in_raises_on_v1_project(self):
        """group_name_not_in must be rejected on WorkflowV1 projects."""
        with pytest.raises(ValueError, match="group_name_not_in"):
            check_asset_workflow_arguments(
                project_workflow_version="V1",
                asset_workflow_filters={"group_name_not_in": ["GroupA"]},
            )

    def test_group_name_not_in_raises_on_v2_project(self):
        """group_name_not_in must be rejected on WorkflowV2 projects (V3-only filter)."""
        with pytest.raises(ValueError, match="group_name_not_in"):
            check_asset_workflow_arguments(
                project_workflow_version="V2",
                asset_workflow_filters={"group_name_not_in": ["GroupA"]},
            )

    def test_group_name_not_in_is_accepted_on_v3_project(self):
        """group_name_not_in must be silently accepted on WorkflowV3 projects."""
        # Should not raise
        check_asset_workflow_arguments(
            project_workflow_version="V3",
            asset_workflow_filters={"group_name_not_in": ["GroupA"]},
        )

    def test_group_name_not_in_none_does_not_raise_on_v1(self):
        """None group_name_not_in must not trigger a rejection on V1 projects."""
        # Should not raise
        check_asset_workflow_arguments(
            project_workflow_version="V1",
            asset_workflow_filters={"group_name_not_in": None},
        )
