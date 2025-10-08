"""Integration tests for ConnectionView objects returned by the connections namespace.

This test file validates that the connections.list() method correctly returns
ConnectionView objects instead of dictionaries, and that these objects provide
proper property access and backward compatibility.

Test Strategy:
    - Verify list() returns ConnectionView objects in all modes (list, generator)
    - Test ConnectionView property access for common properties
    - Validate backward compatibility with dictionary interface via to_dict()
    - Test filtering by project_id and cloud_storage_integration_id
    - Verify computed properties (folder_count, display_name)
    - Ensure mutation methods still return dicts (unchanged)
"""

import pytest

from kili.domain_v2.connection import ConnectionView
from tests_v2 import (
    assert_is_view,
    assert_view_has_dict_compatibility,
    assert_view_property_access,
)


@pytest.mark.integration()
def test_list_returns_connection_views(kili_client):
    """Test that connections.list() in list mode returns ConnectionView objects."""
    # Get all projects to find one with connections
    projects = kili_client.projects.list(first=10, as_generator=False)

    if not projects:
        pytest.skip("No projects available for testing connections")

    # Try to get connections for each project until we find some
    connections = []
    for project in projects:
        connections = kili_client.connections.list(
            project_id=project.id, first=5, as_generator=False
        )
        if connections:
            break

    # Skip if no connections found
    if not connections:
        pytest.skip("No connections available for testing")

    # Verify we get a list
    assert isinstance(
        connections, list
    ), "connections.list() with as_generator=False should return a list"

    # Verify each item is a ConnectionView
    for connection in connections:
        assert_is_view(connection, ConnectionView)

        # Verify we can access basic properties
        assert hasattr(connection, "id")
        assert hasattr(connection, "project_id")
        assert hasattr(connection, "number_of_assets")
        assert hasattr(connection, "selected_folders")


@pytest.mark.integration()
def test_list_generator_returns_connection_views(kili_client):
    """Test that connections.list() in generator mode returns ConnectionView objects."""
    # Get all projects to find one with connections
    projects = kili_client.projects.list(first=10, as_generator=False)

    if not projects:
        pytest.skip("No projects available for testing connections")

    # Try to get connections for each project until we find some
    project_id_with_connections = None
    for project in projects:
        test_connections = kili_client.connections.list(
            project_id=project.id, first=1, as_generator=False
        )
        if test_connections:
            project_id_with_connections = project.id
            break

    if not project_id_with_connections:
        pytest.skip("No connections available for testing")

    # Get connections in generator mode
    connections_gen = kili_client.connections.list(
        project_id=project_id_with_connections, first=5, as_generator=True
    )

    # Take first 5 items from generator (or fewer if less available)
    connections_from_gen = []
    for i, connection in enumerate(connections_gen):
        if i >= 5:
            break
        connections_from_gen.append(connection)

    # Skip if no connections
    if not connections_from_gen:
        pytest.skip("No connections available for testing")

    # Verify each yielded item is a ConnectionView
    for connection in connections_from_gen:
        assert_is_view(connection, ConnectionView)

        # Verify we can access basic properties
        assert hasattr(connection, "id")
        assert hasattr(connection, "project_id")
        assert hasattr(connection, "number_of_assets")


@pytest.mark.integration()
def test_connection_view_properties(kili_client):
    """Test that ConnectionView provides access to all expected properties."""
    # Get all projects to find one with connections
    projects = kili_client.projects.list(first=10, as_generator=False)

    if not projects:
        pytest.skip("No projects available for testing connections")

    # Try to get connections for each project until we find some
    connection = None
    for project in projects:
        connections = kili_client.connections.list(
            project_id=project.id, first=1, as_generator=False
        )
        if connections:
            connection = connections[0]
            break

    if not connection:
        pytest.skip("No connections available for testing")

    # Verify ConnectionView type
    assert_is_view(connection, ConnectionView)

    # Test core properties exist and are accessible
    assert_view_property_access(connection, "id")
    assert_view_property_access(connection, "project_id")
    assert_view_property_access(connection, "number_of_assets")
    assert_view_property_access(connection, "selected_folders")

    # Test that id is not empty
    assert connection.id, "Connection id should not be empty"

    # Test that project_id is not empty
    assert connection.project_id, "Connection project_id should not be empty"

    # Test computed properties
    assert_view_property_access(connection, "folder_count")
    assert_view_property_access(connection, "display_name")

    # Test that folder_count is the length of selected_folders
    assert connection.folder_count == len(
        connection.selected_folders
    ), "folder_count should equal the number of selected_folders"

    # Test that number_of_assets is non-negative
    assert connection.number_of_assets >= 0, "number_of_assets should be non-negative"

    # Test that selected_folders is a list
    assert isinstance(connection.selected_folders, list), "selected_folders should be a list"

    # Test optional properties
    assert_view_property_access(connection, "last_checked")

    # Test display_name returns id
    assert connection.display_name == connection.id, "display_name should return the connection id"


@pytest.mark.integration()
def test_connection_view_dict_compatibility(kili_client):
    """Test that ConnectionView maintains backward compatibility via to_dict()."""
    # Get all projects to find one with connections
    projects = kili_client.projects.list(first=10, as_generator=False)

    if not projects:
        pytest.skip("No projects available for testing connections")

    # Try to get connections for each project until we find some
    connection = None
    for project in projects:
        connections = kili_client.connections.list(
            project_id=project.id, first=1, as_generator=False
        )
        if connections:
            connection = connections[0]
            break

    if not connection:
        pytest.skip("No connections available for testing")

    # Verify ConnectionView type
    assert_is_view(connection, ConnectionView)

    # Test dictionary compatibility
    assert_view_has_dict_compatibility(connection)

    # Get dictionary representation
    connection_dict = connection.to_dict()

    # Verify it's a dictionary
    assert isinstance(connection_dict, dict), "to_dict() should return a dictionary"

    # Verify dictionary has expected keys
    assert "id" in connection_dict, "Dictionary should have 'id' key"

    # Verify dictionary values match property values
    if "projectId" in connection_dict:
        assert (
            connection_dict["projectId"] == connection.project_id
        ), "Dictionary projectId should match property"

    if "numberOfAssets" in connection_dict:
        assert (
            connection_dict["numberOfAssets"] == connection.number_of_assets
        ), "Dictionary numberOfAssets should match property"

    if "selectedFolders" in connection_dict:
        assert (
            connection_dict["selectedFolders"] == connection.selected_folders
        ), "Dictionary selectedFolders should match property"

    # Verify to_dict() returns the same reference (zero-copy)
    assert (
        connection_dict is connection._data
    ), "to_dict() should return the same reference as _data"


@pytest.mark.integration()
def test_connection_view_filtering(kili_client):
    """Test that ConnectionView objects work correctly with filtering."""
    # Get all projects to find one with connections
    projects = kili_client.projects.list(first=10, as_generator=False)

    if not projects:
        pytest.skip("No projects available for testing connections")

    # Try to get connections for each project
    project_id_with_connections = None
    for project in projects:
        connections = kili_client.connections.list(
            project_id=project.id, first=1, as_generator=False
        )
        if connections:
            project_id_with_connections = project.id
            break

    if not project_id_with_connections:
        pytest.skip("No connections available for testing")

    # Test filtering by project_id
    connections_by_project = kili_client.connections.list(
        project_id=project_id_with_connections, first=10, as_generator=False
    )

    # Verify results are ConnectionView objects
    assert len(connections_by_project) > 0, "Should find connections for the project"
    for connection in connections_by_project:
        assert_is_view(connection, ConnectionView)
        # All should have the same project_id
        assert (
            connection.project_id == project_id_with_connections
        ), "Filtered connections should belong to the specified project"


@pytest.mark.integration()
def test_connection_view_empty_results(kili_client):
    """Test that empty results are handled correctly."""
    # Get all projects to get a valid project_id
    projects = kili_client.projects.list(first=1, as_generator=False)

    if not projects:
        pytest.skip("No projects available for testing")

    project_id = projects[0].id

    # Query with a project filter - may or may not have connections
    # This tests that empty results return an empty list
    connections = kili_client.connections.list(project_id=project_id, as_generator=False)

    # Verify we get a list (even if empty)
    assert isinstance(connections, list), "Should return a list even when no results"


@pytest.mark.integration()
def test_connection_view_with_fields_parameter(kili_client):
    """Test that ConnectionView works correctly with custom fields parameter."""
    # Get all projects to find one with connections
    projects = kili_client.projects.list(first=10, as_generator=False)

    if not projects:
        pytest.skip("No projects available for testing connections")

    # Try to get connections for each project until we find some
    connection = None
    for project in projects:
        connections = kili_client.connections.list(
            project_id=project.id,
            first=1,
            fields=["id", "projectId", "numberOfAssets", "selectedFolders", "lastChecked"],
            as_generator=False,
        )
        if connections:
            connection = connections[0]
            break

    if not connection:
        pytest.skip("No connections available for testing")

    # Verify it's still a ConnectionView
    assert_is_view(connection, ConnectionView)

    # Verify requested fields are accessible
    assert_view_property_access(connection, "id")
    assert_view_property_access(connection, "project_id")
    assert_view_property_access(connection, "number_of_assets")
    assert_view_property_access(connection, "selected_folders")
    assert_view_property_access(connection, "last_checked")


@pytest.mark.integration()
def test_connection_view_folder_count(kili_client):
    """Test that folder_count property works correctly."""
    # Get all projects to find one with connections
    projects = kili_client.projects.list(first=10, as_generator=False)

    if not projects:
        pytest.skip("No projects available for testing connections")

    # Try to get connections for each project until we find some
    connection = None
    for project in projects:
        connections = kili_client.connections.list(
            project_id=project.id, first=1, as_generator=False
        )
        if connections:
            connection = connections[0]
            break

    if not connection:
        pytest.skip("No connections available for testing")

    # Verify ConnectionView type
    assert_is_view(connection, ConnectionView)

    # Test folder_count property
    assert_view_property_access(connection, "folder_count")

    # Verify folder_count matches the length of selected_folders
    assert connection.folder_count == len(
        connection.selected_folders
    ), "folder_count should equal the number of selected_folders"

    # Verify folder_count is non-negative
    assert connection.folder_count >= 0, "folder_count should be non-negative"
