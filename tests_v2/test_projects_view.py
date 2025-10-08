"""Integration tests for ProjectView objects returned by the projects namespace.

This test file validates that the projects.list() method correctly returns
ProjectView objects instead of dictionaries, and that these objects provide
proper property access and backward compatibility.

Test Strategy:
    - Verify list() returns ProjectView objects in all modes (list, generator)
    - Test ProjectView property access for common properties
    - Validate backward compatibility with dictionary interface via to_dict()
    - Ensure nested namespaces handle views appropriately
    - Test workflow-related properties for V2 projects
"""

import pytest

from kili.domain_v2.project import ProjectRoleView, ProjectView
from tests_v2 import (
    assert_is_view,
    assert_view_has_dict_compatibility,
    assert_view_property_access,
)


@pytest.mark.integration()
def test_list_returns_project_views(kili_client):
    """Test that projects.list() in list mode returns ProjectView objects."""
    # Get projects in list mode
    projects = kili_client.projects.list(first=5, as_generator=False)

    # Verify we get a list
    assert isinstance(
        projects, list
    ), "projects.list() with as_generator=False should return a list"

    # Skip if no projects
    if not projects:
        pytest.skip("No projects available for testing")

    # Verify each item is a ProjectView
    for project in projects:
        assert_is_view(project, ProjectView)

        # Verify we can access basic properties
        assert hasattr(project, "id")
        assert hasattr(project, "title")
        assert hasattr(project, "display_name")


@pytest.mark.integration()
def test_list_generator_returns_project_views(kili_client):
    """Test that projects.list() in generator mode returns ProjectView objects."""
    # Get projects in generator mode
    projects_gen = kili_client.projects.list(first=5, as_generator=True)

    # Take first 5 items from generator (or fewer if less available)
    projects_from_gen = []
    for i, project in enumerate(projects_gen):
        if i >= 5:
            break
        projects_from_gen.append(project)

    # Skip if no projects
    if not projects_from_gen:
        pytest.skip("No projects available for testing")

    # Verify each yielded item is a ProjectView
    for project in projects_from_gen:
        assert_is_view(project, ProjectView)

        # Verify we can access basic properties
        assert hasattr(project, "id")
        assert hasattr(project, "title")


@pytest.mark.integration()
def test_project_view_properties(kili_client):
    """Test that ProjectView provides access to all expected properties."""
    # Get first project
    projects = kili_client.projects.list(first=1, as_generator=False)

    if not projects:
        pytest.skip("No projects available for testing")

    project = projects[0]

    # Verify ProjectView type
    assert_is_view(project, ProjectView)

    # Test core properties exist and are accessible
    assert_view_property_access(project, "id")
    assert_view_property_access(project, "title")
    assert_view_property_access(project, "description")
    assert_view_property_access(project, "input_type")
    assert_view_property_access(project, "json_interface")
    assert_view_property_access(project, "display_name")

    # Test that id is not empty
    assert project.id, "Project id should not be empty"

    # Test display_name logic (should be title if available, else id)
    if project.title:
        assert project.display_name == project.title
    else:
        assert project.display_name == project.id

    # Test optional properties
    assert_view_property_access(project, "workflow_version")
    assert_view_property_access(project, "steps")
    assert_view_property_access(project, "roles")
    assert_view_property_access(project, "number_of_assets")
    assert_view_property_access(project, "number_of_remaining_assets")
    assert_view_property_access(project, "number_of_reviewed_assets")
    assert_view_property_access(project, "created_at")
    assert_view_property_access(project, "updated_at")
    assert_view_property_access(project, "archived")
    assert_view_property_access(project, "starred")

    # Test computed properties
    assert_view_property_access(project, "is_v2_workflow")
    assert_view_property_access(project, "has_honeypot")
    assert_view_property_access(project, "progress_percentage")

    # Verify steps is a list
    assert isinstance(project.steps, list), "steps property should return a list"

    # Verify roles is a list
    assert isinstance(project.roles, list), "roles property should return a list"

    # Verify progress_percentage is a float
    assert isinstance(project.progress_percentage, float), "progress_percentage should be a float"
    assert (
        0 <= project.progress_percentage <= 100
    ), "progress_percentage should be between 0 and 100"


@pytest.mark.integration()
def test_project_view_dict_compatibility(kili_client):
    """Test that ProjectView maintains backward compatibility via to_dict()."""
    # Get first project
    projects = kili_client.projects.list(first=1, as_generator=False)

    if not projects:
        pytest.skip("No projects available for testing")

    project = projects[0]

    # Verify ProjectView type
    assert_is_view(project, ProjectView)

    # Test dictionary compatibility
    assert_view_has_dict_compatibility(project)

    # Get dictionary representation
    project_dict = project.to_dict()

    # Verify it's a dictionary
    assert isinstance(project_dict, dict), "to_dict() should return a dictionary"

    # Verify dictionary has expected keys
    assert "id" in project_dict, "Dictionary should have 'id' key"

    # Verify dictionary values match property values
    if "title" in project_dict:
        assert project_dict["title"] == project.title, "Dictionary title should match property"

    if "inputType" in project_dict:
        assert (
            project_dict["inputType"] == project.input_type
        ), "Dictionary inputType should match property"

    if "jsonInterface" in project_dict:
        assert (
            project_dict["jsonInterface"] == project.json_interface
        ), "Dictionary jsonInterface should match property"

    # Verify to_dict() returns the same reference (zero-copy)
    assert project_dict is project._data, "to_dict() should return the same reference as _data"


@pytest.mark.integration()
def test_project_view_filtering(kili_client):
    """Test that ProjectView objects work correctly with filtering."""
    # Get all projects
    all_projects = kili_client.projects.list(first=10, as_generator=False)

    if not all_projects:
        pytest.skip("No projects available for testing")

    # Get the first project's ID
    first_project_id = all_projects[0].id

    # Query for specific project by ID
    filtered_projects = kili_client.projects.list(project_id=first_project_id, as_generator=False)

    # Verify we got results
    assert len(filtered_projects) > 0, "Should get at least one project with specific project_id"

    # Verify each result is a ProjectView
    for project in filtered_projects:
        assert_is_view(project, ProjectView)

        # Verify it's the correct project
        assert project.id == first_project_id, "Filtered project should have the requested ID"


@pytest.mark.integration()
def test_project_view_workflow_properties(kili_client):
    """Test ProjectView workflow-related properties for V2 projects."""
    # Get projects
    projects = kili_client.projects.list(first=10, as_generator=False)

    if not projects:
        pytest.skip("No projects available for testing")

    # Find a V2 workflow project if available
    v2_project = None
    for project in projects:
        if project.is_v2_workflow:
            v2_project = project
            break

    if v2_project is None:
        pytest.skip("No V2 workflow projects available for testing")

    # Verify V2 project has steps
    assert_view_property_access(v2_project, "steps")
    assert isinstance(v2_project.steps, list), "V2 project should have steps as a list"

    # Verify workflow_version property
    assert v2_project.workflow_version == "V2", "V2 project should have workflow_version='V2'"

    # Verify is_v2_workflow computed property
    assert v2_project.is_v2_workflow is True, "is_v2_workflow should be True for V2 projects"


@pytest.mark.integration()
def test_users_namespace_still_returns_dicts(kili_client):
    """Test that projects.users.list() returns ProjectRoleView objects."""
    # Get first project
    projects = kili_client.projects.list(first=1, as_generator=False)

    if not projects:
        pytest.skip("No projects available for testing")

    project = projects[0]

    # Get project users
    users = kili_client.projects.users.list(project_id=project.id, first=5, as_generator=False)

    # Verify we get a list
    assert isinstance(users, list), "projects.users.list() should return a list"

    # Skip if no users
    if not users:
        pytest.skip(f"No users available in project {project.id}")

    # Verify each item is a ProjectRoleView (not a dict or ProjectView)
    for user in users:
        assert_is_view(user, ProjectRoleView)
        assert not isinstance(
            user, ProjectView
        ), "projects.users.list() should NOT return ProjectView objects"

        # Verify it has the expected properties
        assert hasattr(user, "id"), "ProjectRoleView should have an id property"
        assert hasattr(user, "role"), "ProjectRoleView should have a role property"
        assert hasattr(user, "user_email"), "ProjectRoleView should have a user_email property"


@pytest.mark.integration()
def test_project_view_empty_results(kili_client):
    """Test that empty results are handled correctly."""
    # Get projects with archived filter
    # Use a filter combination that may return no results
    empty_projects = kili_client.projects.list(
        archived=True, starred=True, first=1, as_generator=False
    )

    # Verify we get a list (may be empty)
    assert isinstance(empty_projects, list), "Should return a list even when no results"

    # If we got results, verify they are ProjectView objects
    for project in empty_projects:
        assert_is_view(project, ProjectView)


@pytest.mark.integration()
def test_project_view_with_fields_parameter(kili_client):
    """Test that ProjectView works correctly with custom fields parameter."""
    # Query with specific fields
    projects = kili_client.projects.list(
        first=1, fields=["id", "title", "inputType", "jsonInterface"], as_generator=False
    )

    if not projects:
        pytest.skip("No projects available for testing")

    project = projects[0]

    # Verify it's still a ProjectView
    assert_is_view(project, ProjectView)

    # Verify requested fields are accessible
    assert_view_property_access(project, "id")
    assert_view_property_access(project, "title")
    assert_view_property_access(project, "input_type")
    assert_view_property_access(project, "json_interface")


@pytest.mark.integration()
def test_project_view_archived_filter(kili_client):
    """Test that ProjectView works correctly with archived filter."""
    # Get only active (non-archived) projects
    active_projects = kili_client.projects.list(archived=False, first=5, as_generator=False)

    # Skip if no active projects
    if not active_projects:
        pytest.skip("No active projects available for testing")

    # Verify each project is a ProjectView and is not archived
    for project in active_projects:
        assert_is_view(project, ProjectView)
        assert (
            project.archived is False
        ), "Project should not be archived when filtered with archived=False"


@pytest.mark.integration()
def test_project_view_progress_calculation(kili_client):
    """Test that ProjectView calculates progress percentage correctly."""
    # Get first project
    projects = kili_client.projects.list(first=1, as_generator=False)

    if not projects:
        pytest.skip("No projects available for testing")

    project = projects[0]

    # Verify ProjectView type
    assert_is_view(project, ProjectView)

    # Get progress percentage
    progress = project.progress_percentage

    # Verify progress is a valid percentage
    assert isinstance(progress, float), "progress_percentage should be a float"
    assert 0 <= progress <= 100, f"progress_percentage should be between 0 and 100, got {progress}"

    # Verify progress calculation logic
    total = project.number_of_assets
    remaining = project.number_of_remaining_assets

    if total == 0:
        assert progress == 0.0, "progress should be 0 when total assets is 0"
    else:
        completed = total - remaining
        expected_progress = (completed / total) * 100
        assert (
            abs(progress - expected_progress) < 0.01
        ), f"progress calculation incorrect: expected {expected_progress}, got {progress}"
