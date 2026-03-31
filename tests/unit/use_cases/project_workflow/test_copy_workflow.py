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


_DEST_USERS = [
    {"role": "REVIEWER", "user": {"id": "user-reviewer-1"}},
    {"role": "LABELER", "user": {"id": "user-labeler-1"}},
    {"role": "REVIEWER", "user": {"id": "user-reviewer-2"}},
]
_LABELER_IDS = ["user-reviewer-1", "user-labeler-1", "user-reviewer-2"]
_REVIEWER_IDS = ["user-reviewer-1", "user-reviewer-2"]  # role != LABELER


def _setup_happy_path(mock_gateway, *, enforce_step_separation: bool | None = None) -> None:
    """Configure common gateway mocks for tests that pass all validations."""
    mock_gateway.get_project.side_effect = [
        {"enforceStepSeparation": enforce_step_separation},  # source project fetch
        {"workflowVersion": "V2"},  # destination V2 validation
    ]
    mock_gateway.count_labels.return_value = 0
    # >= numberOfExpectedLabelsForConsensus (3)
    mock_gateway.count_activated_project_users.return_value = 3
    mock_gateway.list_activated_project_users.return_value = _DEST_USERS


class TestCopyWorkflowFromProject:
    """Tests for copy_workflow_from_project."""

    def test_copies_basic_workflow(self, use_cases, mock_gateway):
        """Test copying a basic workflow: first dest step is updated, remaining are created."""
        source_id = ProjectId("source-project")
        dest_id = ProjectId("dest-project")

        mock_gateway.get_steps.side_effect = [
            _make_source_steps(),  # source steps
            [{"id": "dest-step-old", "name": "Old Step"}],  # dest steps (1 step)
        ]
        _setup_happy_path(mock_gateway)
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

        # First source step → update the existing first dest step
        assert data.update_steps is not None and len(data.update_steps) == 1
        assert data.update_steps[0]["id"] == "dest-step-old"
        assert data.update_steps[0]["name"] == "Labeling"
        assert data.update_steps[0]["consensus_coverage"] == 50

        # Remaining source steps → create new
        assert data.create_steps is not None and len(data.create_steps) == 1
        assert data.create_steps[0]["name"] == "Review"
        assert data.create_steps[0]["type"] == "REVIEW"
        assert data.create_steps[0]["step_coverage"] == 80

        # No dest steps to delete (only 1 dest step, which was updated)
        assert data.delete_steps is None

    def test_copies_enforce_step_separation(self, use_cases, mock_gateway):
        """Test that enforce_step_separation is copied from the source project."""
        source_id = ProjectId("source-project")
        dest_id = ProjectId("dest-project")

        mock_gateway.get_steps.side_effect = [
            _make_source_steps(),
            [{"id": "dest-step-old", "name": "Old Step"}],
        ]
        _setup_happy_path(mock_gateway, enforce_step_separation=True)
        mock_gateway.update_project_workflow.return_value = {
            "editProjectWorkflowSettings": {"steps": []}
        }

        use_cases.copy_workflow_from_project(
            source_project_id=source_id,
            destination_project_id=dest_id,
        )

        update_call = mock_gateway.update_project_workflow.call_args
        data = update_call[0][1]
        assert data.enforce_step_separation is True

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

    def test_raises_when_destination_is_not_workflow_v2(self, use_cases, mock_gateway):
        """Test that ValueError is raised when destination project is not workflow V2."""
        source_id = ProjectId("source-project")
        dest_id = ProjectId("dest-project")

        mock_gateway.get_steps.return_value = _make_source_steps()
        mock_gateway.get_project.side_effect = [
            {"enforceStepSeparation": None},  # source project fetch
            {"workflowVersion": "V1"},  # destination V2 validation
        ]

        with pytest.raises(ValueError, match="workflow version"):
            use_cases.copy_workflow_from_project(
                source_project_id=source_id,
                destination_project_id=dest_id,
            )

    def test_raises_when_destination_has_labels(self, use_cases, mock_gateway):
        """Test that ValueError is raised when destination has labels."""
        source_id = ProjectId("source-project")
        dest_id = ProjectId("dest-project")

        mock_gateway.get_steps.return_value = _make_source_steps()
        mock_gateway.get_project.side_effect = [
            {"enforceStepSeparation": None},
            {"workflowVersion": "V2"},
        ]
        mock_gateway.count_labels.return_value = 5

        with pytest.raises(ValueError, match="already has 5 label"):
            use_cases.copy_workflow_from_project(
                source_project_id=source_id,
                destination_project_id=dest_id,
            )

    def test_raises_when_destination_has_too_few_labelers(self, use_cases, mock_gateway):
        """Test that ValueError is raised when destination lacks labelers for consensus."""
        source_id = ProjectId("source-project")
        dest_id = ProjectId("dest-project")

        mock_gateway.get_steps.return_value = _make_source_steps()  # first step requires 3
        mock_gateway.get_project.side_effect = [
            {"enforceStepSeparation": None},
            {"workflowVersion": "V2"},
        ]
        mock_gateway.count_labels.return_value = 0
        # 2 is fewer than the required 3
        mock_gateway.count_activated_project_users.return_value = 2

        with pytest.raises(ValueError, match="2 activated labeler"):
            use_cases.copy_workflow_from_project(
                source_project_id=source_id,
                destination_project_id=dest_id,
            )

    def test_raises_when_later_step_requires_more_labelers(self, use_cases, mock_gateway):
        """Test that validation checks all steps, not just the first one."""
        source_id = ProjectId("source-project")
        dest_id = ProjectId("dest-project")

        # First step: no consensus; second step: requires 5 labelers
        steps = [
            {
                "id": "source-step-1",
                "name": "Labeling",
                "type": "DEFAULT",
                "consensusCoverage": None,
                "numberOfExpectedLabelsForConsensus": None,
                "stepCoverage": None,
                "sendBackStepId": None,
            },
            {
                "id": "source-step-2",
                "name": "Second Pass",
                "type": "DEFAULT",
                "consensusCoverage": 80,
                "numberOfExpectedLabelsForConsensus": 5,
                "stepCoverage": None,
                "sendBackStepId": None,
            },
        ]
        mock_gateway.get_steps.return_value = steps
        mock_gateway.get_project.side_effect = [
            {"enforceStepSeparation": None},
            {"workflowVersion": "V2"},
        ]
        mock_gateway.count_labels.return_value = 0
        mock_gateway.count_activated_project_users.return_value = 3  # fewer than 5

        with pytest.raises(ValueError, match="3 activated labeler"):
            use_cases.copy_workflow_from_project(
                source_project_id=source_id,
                destination_project_id=dest_id,
            )

    def test_skips_consensus_check_when_not_set(self, use_cases, mock_gateway):
        """Test consensus labeler check is skipped when numberOfExpectedLabelsForConsensus is None."""
        source_id = ProjectId("source-project")
        dest_id = ProjectId("dest-project")

        steps_without_consensus = [
            {
                "id": "source-step-1",
                "name": "Labeling",
                "type": "DEFAULT",
                "consensusCoverage": None,
                "numberOfExpectedLabelsForConsensus": None,
                "stepCoverage": None,
                "sendBackStepId": None,
            }
        ]
        mock_gateway.get_steps.side_effect = [
            steps_without_consensus,
            [{"id": "dest-old", "name": "Old"}],
        ]
        mock_gateway.get_project.side_effect = [
            {"enforceStepSeparation": None},
            {"workflowVersion": "V2"},
        ]
        mock_gateway.count_labels.return_value = 0
        mock_gateway.update_project_workflow.return_value = {
            "editProjectWorkflowSettings": {"steps": []}
        }

        use_cases.copy_workflow_from_project(
            source_project_id=source_id,
            destination_project_id=dest_id,
        )

        mock_gateway.count_activated_project_users.assert_not_called()

    def test_remaps_send_back_step_id(self, use_cases, mock_gateway):
        """Test that sendBackStepId is remapped to new step IDs."""
        source_id = ProjectId("source-project")
        dest_id = ProjectId("dest-project")

        mock_gateway.get_steps.side_effect = [
            _make_source_steps(with_send_back=True),
            [{"id": "dest-old", "name": "OldStep"}],  # 1 existing dest step
            # After update+create, dest has: updated first step + new Review step
            [
                {"id": "dest-old", "name": "Labeling"},
                {"id": "new-step-2", "name": "Review"},
            ],
        ]
        _setup_happy_path(mock_gateway)
        mock_gateway.update_project_workflow.return_value = {
            "editProjectWorkflowSettings": {"steps": []}
        }

        use_cases.copy_workflow_from_project(
            source_project_id=source_id,
            destination_project_id=dest_id,
        )

        # Should have been called twice: once for update/create, once for sendBackStepId remap
        assert mock_gateway.update_project_workflow.call_count == 2

        # Verify the second call remaps sendBackStepId
        second_call = mock_gateway.update_project_workflow.call_args_list[1]
        data = second_call[0][1]
        assert data.update_steps is not None
        assert len(data.update_steps) == 1
        # Review step's sendBackStepId should point to Labeling (dest-old)
        assert data.update_steps[0]["id"] == "new-step-2"
        assert data.update_steps[0]["send_back_step_id"] == "dest-old"

    def test_deletes_extra_dest_steps(self, use_cases, mock_gateway):
        """Test that extra dest steps beyond the first are deleted."""
        source_id = ProjectId("source-project")
        dest_id = ProjectId("dest-project")

        mock_gateway.get_steps.side_effect = [
            _make_source_steps(),  # source: 2 steps
            [  # dest: 3 existing steps
                {"id": "dest-step-1", "name": "Step1"},
                {"id": "dest-step-2", "name": "Step2"},
                {"id": "dest-step-3", "name": "Step3"},
            ],
        ]
        _setup_happy_path(mock_gateway)
        mock_gateway.update_project_workflow.return_value = {
            "editProjectWorkflowSettings": {"steps": []}
        }

        use_cases.copy_workflow_from_project(
            source_project_id=source_id,
            destination_project_id=dest_id,
        )

        update_call = mock_gateway.update_project_workflow.call_args
        data = update_call[0][1]
        # First dest step updated, other two deleted
        assert data.update_steps is not None and data.update_steps[0]["id"] == "dest-step-1"
        assert set(data.delete_steps) == {"dest-step-2", "dest-step-3"}

    def test_handles_destination_without_existing_workflow(self, use_cases, mock_gateway):
        """Test copying to a project that has no existing workflow (creates all steps)."""
        source_id = ProjectId("source-project")
        dest_id = ProjectId("dest-project")

        def get_steps_side_effect(project_id, _fields) -> list:
            if project_id == source_id:
                return _make_source_steps()
            raise ValueError("No workflow found")

        mock_gateway.get_steps.side_effect = get_steps_side_effect
        _setup_happy_path(mock_gateway)
        mock_gateway.update_project_workflow.return_value = {
            "editProjectWorkflowSettings": {"steps": []}
        }

        use_cases.copy_workflow_from_project(
            source_project_id=source_id,
            destination_project_id=dest_id,
        )

        update_call = mock_gateway.update_project_workflow.call_args
        data = update_call[0][1]
        # No dest steps → create all, no updates, no deletes
        assert data.update_steps is None
        assert data.create_steps is not None and len(data.create_steps) == 2
        assert data.delete_steps is None

    def test_assignees_use_dest_project_users(self, use_cases, mock_gateway):
        """Test that created steps use destination project users, not source assignees."""
        source_id = ProjectId("source-project")
        dest_id = ProjectId("dest-project")

        mock_gateway.get_steps.side_effect = [
            _make_source_steps(),  # source: DEFAULT + REVIEW
            [{"id": "dest-old", "name": "Old"}],
        ]
        _setup_happy_path(mock_gateway)
        mock_gateway.update_project_workflow.return_value = {
            "editProjectWorkflowSettings": {"steps": []}
        }

        use_cases.copy_workflow_from_project(
            source_project_id=source_id,
            destination_project_id=dest_id,
        )

        update_call = mock_gateway.update_project_workflow.call_args
        data = update_call[0][1]

        # update_steps (first DEFAULT step): no assignees on update
        assert data.update_steps is not None
        assert "assignees" not in data.update_steps[0]

        # create_steps (REVIEW step): reviewer_ids only (role != LABELER)
        assert data.create_steps is not None
        assert data.create_steps[0]["assignees"] == _REVIEWER_IDS

    def test_raises_when_source_and_destination_are_same(self, use_cases):
        """Test that ValueError is raised when source and destination are the same project."""
        project_id = ProjectId("same-project")

        with pytest.raises(ValueError, match="must be different"):
            use_cases.copy_workflow_from_project(
                source_project_id=project_id,
                destination_project_id=project_id,
            )

    def test_raises_when_source_has_duplicate_step_names(self, use_cases, mock_gateway):
        """Test that ValueError is raised when source has duplicate step names."""
        source_id = ProjectId("source-project")
        dest_id = ProjectId("dest-project")

        duplicate_steps = [
            {
                "id": "step-1",
                "name": "Labeling",
                "type": "DEFAULT",
                "consensusCoverage": None,
                "numberOfExpectedLabelsForConsensus": None,
                "stepCoverage": None,
                "sendBackStepId": None,
            },
            {
                "id": "step-2",
                "name": "Labeling",
                "type": "DEFAULT",
                "consensusCoverage": None,
                "numberOfExpectedLabelsForConsensus": None,
                "stepCoverage": None,
                "sendBackStepId": None,
            },
        ]
        mock_gateway.get_steps.return_value = duplicate_steps

        with pytest.raises(ValueError, match="duplicate step names"):
            use_cases.copy_workflow_from_project(
                source_project_id=source_id,
                destination_project_id=dest_id,
            )
