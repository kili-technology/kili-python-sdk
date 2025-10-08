"""Unit tests for Project domain contracts."""

from typing import cast

from kili.domain_v2.project import (
    ProjectContract,
    ProjectView,
    get_ordered_steps,
    get_step_by_name,
    validate_project,
)


class TestProjectContract:
    """Test suite for ProjectContract."""

    def test_validate_project_with_valid_data(self):
        """Test validating a valid project contract."""
        project_data = {
            "id": "project-123",
            "title": "My Project",
            "description": "Test project",
            "inputType": "IMAGE",
            "jsonInterface": {},
            "workflowVersion": "V2",
            "steps": [],
            "roles": [],
            "numberOfAssets": 100,
            "archived": False,
            "createdAt": "2024-01-01T00:00:00Z",
        }

        result = validate_project(project_data)
        assert result == project_data

    def test_validate_project_with_partial_data(self):
        """Test validating a project with only some fields."""
        project_data = {
            "id": "project-123",
            "title": "My Project",
        }

        result = validate_project(project_data)
        assert result == project_data

    def test_validate_project_with_workflow_steps(self):
        """Test validating a project with workflow v2 steps."""
        project_data = {
            "id": "project-123",
            "title": "My Project",
            "workflowVersion": "V2",
            "steps": [
                {
                    "id": "step-1",
                    "name": "Labeling",
                    "type": "DEFAULT",
                    "order": 0,
                },
                {
                    "id": "step-2",
                    "name": "Review",
                    "type": "REVIEW",
                    "order": 1,
                },
            ],
        }

        result = validate_project(project_data)
        assert result == project_data
        assert len(result.get("steps", [])) == 2


class TestProjectView:
    """Test suite for ProjectView wrapper."""

    def test_project_view_basic_properties(self):
        """Test basic property access on ProjectView."""
        project_data = cast(
            ProjectContract,
            {
                "id": "project-123",
                "title": "My Project",
                "description": "Test description",
                "inputType": "IMAGE",
                "numberOfAssets": 100,
                "archived": False,
                "starred": True,
            },
        )

        view = ProjectView(project_data)

        assert view.id == "project-123"
        assert view.title == "My Project"
        assert view.description == "Test description"
        assert view.input_type == "IMAGE"
        assert view.number_of_assets == 100
        assert view.archived is False
        assert view.starred is True

    def test_project_view_display_name(self):
        """Test display name property."""
        # With title
        project_data = cast(ProjectContract, {"id": "project-123", "title": "My Project"})
        view = ProjectView(project_data)
        assert view.display_name == "My Project"

        # Without title
        project_data = cast(ProjectContract, {"id": "project-123"})
        view = ProjectView(project_data)
        assert view.display_name == "project-123"

    def test_project_view_workflow_version(self):
        """Test workflow version properties."""
        # V2 workflow
        project_data = cast(ProjectContract, {"id": "project-123", "workflowVersion": "V2"})
        view = ProjectView(project_data)
        assert view.workflow_version == "V2"
        assert view.is_v2_workflow is True

        # V1 workflow
        project_data = cast(ProjectContract, {"id": "project-123", "workflowVersion": "V1"})
        view = ProjectView(project_data)
        assert view.is_v2_workflow is False

    def test_project_view_steps(self):
        """Test steps property."""
        project_data = cast(
            ProjectContract,
            {
                "id": "project-123",
                "steps": [
                    {"id": "step-1", "name": "Label", "order": 0},
                    {"id": "step-2", "name": "Review", "order": 1},
                ],
            },
        )

        view = ProjectView(project_data)

        assert len(view.steps) == 2
        assert view.steps[0].get("name") == "Label"
        assert view.steps[1].get("name") == "Review"

    def test_project_view_roles(self):
        """Test roles property."""
        project_data = cast(
            ProjectContract,
            {
                "id": "project-123",
                "roles": [
                    {"id": "role-1", "role": "ADMIN", "user": {"id": "user-1"}},
                    {"id": "role-2", "role": "LABELER", "user": {"id": "user-2"}},
                ],
            },
        )

        view = ProjectView(project_data)

        assert len(view.roles) == 2
        assert view.roles[0].get("role") == "ADMIN"

    def test_project_view_asset_counts(self):
        """Test asset count properties."""
        project_data = cast(
            ProjectContract,
            {
                "id": "project-123",
                "numberOfAssets": 100,
                "numberOfRemainingAssets": 30,
                "numberOfReviewedAssets": 50,
            },
        )

        view = ProjectView(project_data)

        assert view.number_of_assets == 100
        assert view.number_of_remaining_assets == 30
        assert view.number_of_reviewed_assets == 50

    def test_project_view_progress_percentage(self):
        """Test progress percentage calculation."""
        # 70% complete
        project_data = cast(
            ProjectContract,
            {
                "id": "project-123",
                "numberOfAssets": 100,
                "numberOfRemainingAssets": 30,
            },
        )
        view = ProjectView(project_data)
        assert view.progress_percentage == 70.0

        # Empty project
        project_data = cast(
            ProjectContract,
            {
                "id": "project-123",
                "numberOfAssets": 0,
                "numberOfRemainingAssets": 0,
            },
        )
        view = ProjectView(project_data)
        assert view.progress_percentage == 0.0

        # Fully complete
        project_data = cast(
            ProjectContract,
            {
                "id": "project-123",
                "numberOfAssets": 100,
                "numberOfRemainingAssets": 0,
            },
        )
        view = ProjectView(project_data)
        assert view.progress_percentage == 100.0

    def test_project_view_has_honeypot(self):
        """Test honeypot property."""
        project_data = cast(ProjectContract, {"id": "project-123", "useHoneypot": True})
        view = ProjectView(project_data)
        assert view.has_honeypot is True

        project_data = cast(ProjectContract, {"id": "project-123", "useHoneypot": False})
        view = ProjectView(project_data)
        assert view.has_honeypot is False

    def test_project_view_timestamps(self):
        """Test timestamp properties."""
        project_data = cast(
            ProjectContract,
            {
                "id": "project-123",
                "createdAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-15T10:30:00Z",
            },
        )

        view = ProjectView(project_data)

        assert view.created_at == "2024-01-01T00:00:00Z"
        assert view.updated_at == "2024-01-15T10:30:00Z"

    def test_project_view_json_interface(self):
        """Test JSON interface property."""
        project_data = cast(
            ProjectContract,
            {
                "id": "project-123",
                "jsonInterface": {
                    "jobs": {
                        "JOB_1": {
                            "mlTask": "CLASSIFICATION",
                            "content": {"categories": {"CAT_A": {}}},
                        }
                    }
                },
            },
        )

        view = ProjectView(project_data)

        assert "jobs" in view.json_interface
        assert "JOB_1" in view.json_interface["jobs"]

    def test_project_view_to_dict(self):
        """Test converting view back to dictionary."""
        project_data = cast(
            ProjectContract,
            {
                "id": "project-123",
                "title": "My Project",
                "inputType": "IMAGE",
            },
        )

        view = ProjectView(project_data)
        result = view.to_dict()

        assert result == project_data
        assert result is project_data

    def test_project_view_missing_fields(self):
        """Test accessing missing fields returns appropriate defaults."""
        project_data = cast(ProjectContract, {"id": "project-123"})
        view = ProjectView(project_data)

        assert view.title == ""
        assert view.description == ""
        assert view.input_type is None
        assert view.workflow_version is None
        assert view.steps == []
        assert view.roles == []
        assert view.number_of_assets == 0
        assert view.created_at is None
        assert view.updated_at is None
        assert view.archived is False
        assert view.starred is False


class TestProjectHelpers:
    """Test suite for project helper functions."""

    def test_get_step_by_name_found(self):
        """Test finding a step by name."""
        project = cast(
            ProjectContract,
            {
                "id": "project-123",
                "steps": [
                    {"id": "step-1", "name": "Labeling", "order": 0},
                    {"id": "step-2", "name": "Review", "order": 1},
                    {"id": "step-3", "name": "QA", "order": 2},
                ],
            },
        )

        step = get_step_by_name(project, "Review")

        assert step is not None
        assert step.get("id") == "step-2"
        assert step.get("name") == "Review"

    def test_get_step_by_name_not_found(self):
        """Test step not found returns None."""
        project = cast(
            ProjectContract,
            {
                "id": "project-123",
                "steps": [
                    {"id": "step-1", "name": "Labeling", "order": 0},
                ],
            },
        )

        step = get_step_by_name(project, "NonExistent")

        assert step is None

    def test_get_step_by_name_no_steps(self):
        """Test with project having no steps."""
        project = cast(ProjectContract, {"id": "project-123"})

        step = get_step_by_name(project, "Labeling")

        assert step is None

    def test_get_ordered_steps(self):
        """Test getting steps ordered by their order field."""
        project = cast(
            ProjectContract,
            {
                "id": "project-123",
                "steps": [
                    {"id": "step-2", "name": "Review", "order": 2},
                    {"id": "step-1", "name": "Labeling", "order": 0},
                    {"id": "step-3", "name": "QA", "order": 1},
                ],
            },
        )

        ordered = get_ordered_steps(project)

        assert len(ordered) == 3
        assert ordered[0].get("name") == "Labeling"
        assert ordered[1].get("name") == "QA"
        assert ordered[2].get("name") == "Review"

    def test_get_ordered_steps_empty(self):
        """Test getting ordered steps from empty project."""
        project = cast(ProjectContract, {"id": "project-123"})

        ordered = get_ordered_steps(project)

        assert ordered == []

    def test_get_ordered_steps_missing_order(self):
        """Test ordering steps when some lack order field."""
        project = cast(
            ProjectContract,
            {
                "id": "project-123",
                "steps": [
                    {"id": "step-2", "name": "Review", "order": 1},
                    {"id": "step-1", "name": "Labeling"},  # Missing order
                ],
            },
        )

        ordered = get_ordered_steps(project)

        # Step without order defaults to 0
        assert ordered[0].get("name") == "Labeling"
        assert ordered[1].get("name") == "Review"
