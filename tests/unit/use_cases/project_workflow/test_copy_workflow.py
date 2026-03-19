"""Tests for copy_workflow_from_project use case."""

from unittest.mock import MagicMock

import pytest

from kili.domain.label import LabelFilters
from kili.domain.project import ProjectId
from kili.use_cases.project_workflow import ProjectWorkflowUseCases


@pytest.fixture()
def mock_gateway():
    """Create a mock KiliAPIGateway."""
    return MagicMock()


@pytest.fixture()
def use_cases(mock_gateway):
    """Create ProjectWorkflowUseCases with mocked gateway."""
    return ProjectWorkflowUseCases(mock_gateway)


def _make_source_steps(
    *,
    with_send_back: bool = False,
) -> list[dict]:
    """Create sample source steps."""
    return [
        {
            "id": "source-step-1",
            "name": "Labeling",
            "type": "DEFAULT",
            "consensusCoverage": 50,
            "numberOfExpectedLabelsForConsensus": 3,
            "stepCoverage": None,
            "sendBackStepId": None,
        },
        {
            "id": "source-step-2",
            "name": "Review",
            "type": "REVIEW",
            "consensusCoverage": None,
            "numberOfExpectedLabelsForConsensus": None,
            "stepCoverage": 80,
            "sendBackStepId": "source-step-1" if with_send_back else None,
        },
    ]


class TestCopyWorkflowFromProject:
    """Tests for copy_workflow_from_project."""

    def test_copies_basic_workflow(self, use_cases, mock_gateway):
        """Test copying a basic workflow without sendBackStepId."""
        source_id = ProjectId("source-project")
        dest_id = ProjectId("dest-project")

        mock_gateway.get_steps.side_effect = [
            _make_source_steps(),  # source steps
            [{"id": "dest-step-old", "name": "Old Step"}],  # dest steps
        ]
        mock_gateway.count_labels.return_value = 0
        mock_gateway.update_project_workflow.return_value = {
            "editProjectWorkflowSettings": {"steps": []}
        }

        use_cases.copy_workflow_from_project(
            source_project_id=source_id,
            destination_project_id=dest_id,
        )

        # Verify label count check
        mock_gateway.count_labels.assert_called_once_with(filters=LabelFilters(project_id=dest_id))

        # Verify update call
        update_call = mock_gateway.update_project_workflow.call_args
        assert update_call[0][0] == dest_id
        data = update_call[0][1]
        assert len(data.create_steps) == 2
        assert data.create_steps[0]["name"] == "Labeling"
        assert data.create_steps[0]["type"] == "DEFAULT"
        assert data.create_steps[0]["assignees"] == []
        assert data.create_steps[0]["consensus_coverage"] == 50
        assert data.create_steps[1]["name"] == "Review"
        assert data.create_steps[1]["type"] == "REVIEW"
        assert data.create_steps[1]["step_coverage"] == 80
        assert data.delete_steps == ["dest-step-old"]

    def test_raises_when_source_has_no_steps(self, use_cases, mock_gateway):
        """Test that ValueError is raised when source has no workflow steps."""
        source_id = ProjectId("source-project")
        dest_id = ProjectId("dest-project")

        mock_gateway.get_steps.return_value = []

        with pytest.raises(ValueError, match="has no workflow steps"):
            use_cases.copy_workflow_from_project(
                source_project_id=source_id,
                destination_project_id=dest_id,
            )

    def test_raises_when_destination_has_labels(self, use_cases, mock_gateway):
        """Test that ValueError is raised when destination has labels."""
        source_id = ProjectId("source-project")
        dest_id = ProjectId("dest-project")

        mock_gateway.get_steps.return_value = _make_source_steps()
        mock_gateway.count_labels.return_value = 5

        with pytest.raises(ValueError, match="already has 5 label"):
            use_cases.copy_workflow_from_project(
                source_project_id=source_id,
                destination_project_id=dest_id,
            )

    def test_remaps_send_back_step_id(self, use_cases, mock_gateway):
        """Test that sendBackStepId is remapped to new step IDs."""
        source_id = ProjectId("source-project")
        dest_id = ProjectId("dest-project")

        mock_gateway.get_steps.side_effect = [
            _make_source_steps(with_send_back=True),
            [{"id": "dest-old", "name": "OldStep"}],
            [
                {"id": "new-step-1", "name": "Labeling"},
                {"id": "new-step-2", "name": "Review"},
            ],
        ]
        mock_gateway.count_labels.return_value = 0
        mock_gateway.update_project_workflow.return_value = {
            "editProjectWorkflowSettings": {"steps": []}
        }

        use_cases.copy_workflow_from_project(
            source_project_id=source_id,
            destination_project_id=dest_id,
        )

        # Should have been called twice: once for create, once for sendBackStepId update
        assert mock_gateway.update_project_workflow.call_count == 2

        # Verify the second call remaps sendBackStepId
        second_call = mock_gateway.update_project_workflow.call_args_list[1]
        data = second_call[0][1]
        assert data.update_steps is not None
        assert len(data.update_steps) == 1
        assert data.update_steps[0]["id"] == "new-step-2"
        assert data.update_steps[0]["send_back_step_id"] == "new-step-1"

    def test_handles_destination_without_existing_workflow(self, use_cases, mock_gateway):
        """Test copying to a project that has no existing workflow."""
        source_id = ProjectId("source-project")
        dest_id = ProjectId("dest-project")

        def get_steps_side_effect(project_id, fields) -> list:
            if project_id == source_id:
                return _make_source_steps()
            raise ValueError("No workflow found")

        mock_gateway.get_steps.side_effect = get_steps_side_effect
        mock_gateway.count_labels.return_value = 0
        mock_gateway.update_project_workflow.return_value = {
            "editProjectWorkflowSettings": {"steps": []}
        }

        use_cases.copy_workflow_from_project(
            source_project_id=source_id,
            destination_project_id=dest_id,
        )

        # Verify update was called with no deletes
        update_call = mock_gateway.update_project_workflow.call_args
        data = update_call[0][1]
        assert data.delete_steps is None

    def test_does_not_copy_assignees(self, use_cases, mock_gateway):
        """Test that assignees are not copied from source steps."""
        source_id = ProjectId("source-project")
        dest_id = ProjectId("dest-project")

        mock_gateway.get_steps.side_effect = [
            _make_source_steps(),
            [{"id": "old", "name": "Old"}],
        ]
        mock_gateway.count_labels.return_value = 0
        mock_gateway.update_project_workflow.return_value = {
            "editProjectWorkflowSettings": {"steps": []}
        }

        use_cases.copy_workflow_from_project(
            source_project_id=source_id,
            destination_project_id=dest_id,
        )

        update_call = mock_gateway.update_project_workflow.call_args
        data = update_call[0][1]
        for step in data.create_steps:
            assert step["assignees"] == []
