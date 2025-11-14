"""Tests for the ConnectionsNamespace."""

from unittest.mock import Mock

import pytest

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.domain_api.storages import StoragesNamespace


class TestConnectionsNamespace:
    """Tests for StoragesNamespace functionality."""

    @pytest.fixture()
    def mock_client(self):
        """Create a mock Kili client."""
        client = Mock()
        client.__class__.__name__ = "Kili"
        return client

    @pytest.fixture()
    def mock_gateway(self):
        """Create a mock KiliAPIGateway."""
        return Mock(spec=KiliAPIGateway)

    @pytest.fixture()
    def connections_namespace(self, mock_client, mock_gateway):
        """Create a ConnectionsNamespace instance."""
        return StoragesNamespace(mock_client, mock_gateway).connections

    def test_list_calls_legacy_method(self, connections_namespace, mock_client):
        """Test that list() calls the legacy cloud_storage_connections method."""
        mock_client.cloud_storage_connections.return_value = [
            {"id": "conn_123", "projectId": "proj_456"}
        ]

        result = connections_namespace.list(filter={"project_id": "proj_456"})

        mock_client.cloud_storage_connections.assert_called_once_with(
            cloud_storage_connection_id=None,
            cloud_storage_integration_id=None,
            project_id="proj_456",
            fields=("id", "lastChecked", "numberOfAssets", "selectedFolders", "projectId"),
            first=None,
            skip=0,
            disable_tqdm=None,
            as_generator=False,
        )
        assert result == [{"id": "conn_123", "projectId": "proj_456"}]

    def test_list_parameter_validation(self, connections_namespace, mock_client):
        """Test that list validates required parameters."""
        # Should raise ValueError when no filtering parameters provided
        mock_client.cloud_storage_connections.side_effect = ValueError(
            "At least one of cloud_storage_connection_id, "
            "cloud_storage_integration_id or project_id must be specified"
        )

        with pytest.raises(ValueError, match="At least one of"):
            connections_namespace.list()

    def test_create_calls_legacy_method(self, connections_namespace, mock_client):
        """Test that create() calls the legacy add_cloud_storage_connection method."""
        mock_client.add_cloud_storage_connection.return_value = {"id": "conn_789"}

        result = connections_namespace.create(
            project_id="proj_123", cloud_storage_integration_id="int_456", prefix="data/"
        )

        mock_client.add_cloud_storage_connection.assert_called_once_with(
            project_id="proj_123",
            cloud_storage_integration_id="int_456",
            selected_folders=None,
            prefix="data/",
            include=None,
            exclude=None,
        )
        assert result == {"id": "conn_789"}

    def test_create_input_validation(self, connections_namespace):
        """Test that create() validates input parameters."""
        # Test empty project_id
        with pytest.raises(ValueError, match="project_id cannot be empty"):
            connections_namespace.create(project_id="", cloud_storage_integration_id="int_456")

        # Test whitespace-only project_id
        with pytest.raises(ValueError, match="project_id cannot be empty"):
            connections_namespace.create(project_id="   ", cloud_storage_integration_id="int_456")

        # Test empty cloud_storage_integration_id
        with pytest.raises(ValueError, match="cloud_storage_integration_id cannot be empty"):
            connections_namespace.create(project_id="proj_123", cloud_storage_integration_id="")

        # Test whitespace-only cloud_storage_integration_id
        with pytest.raises(ValueError, match="cloud_storage_integration_id cannot be empty"):
            connections_namespace.create(project_id="proj_123", cloud_storage_integration_id="   ")

    def test_create_error_handling(self, connections_namespace, mock_client):
        """Test that create() provides enhanced error handling."""
        # Test "not found" error enhancement
        mock_client.add_cloud_storage_connection.side_effect = Exception("Project not found")

        with pytest.raises(RuntimeError, match="Failed to create connection.*not found"):
            connections_namespace.create(
                project_id="proj_123", cloud_storage_integration_id="int_456"
            )

        # Test "permission" error enhancement
        mock_client.add_cloud_storage_connection.side_effect = Exception(
            "Access denied: insufficient permissions"
        )

        with pytest.raises(RuntimeError, match="Failed to create connection.*permissions"):
            connections_namespace.create(
                project_id="proj_123", cloud_storage_integration_id="int_456"
            )

    def test_sync_calls_legacy_method(self, connections_namespace, mock_client):
        """Test that sync() calls the legacy synchronize_cloud_storage_connection method."""
        mock_client.synchronize_cloud_storage_connection.return_value = {
            "numberOfAssets": 42,
            "projectId": "proj_123",
        }

        result = connections_namespace.sync(connection_id="conn_789", dry_run=True)

        mock_client.synchronize_cloud_storage_connection.assert_called_once_with(
            cloud_storage_connection_id="conn_789",
            delete_extraneous_files=False,
            dry_run=True,
        )
        assert result == {"numberOfAssets": 42, "projectId": "proj_123"}

    def test_sync_input_validation(self, connections_namespace):
        """Test that sync() validates input parameters."""
        # Test empty connection_id
        with pytest.raises(ValueError, match="connection_id cannot be empty"):
            connections_namespace.sync(connection_id="")

        # Test whitespace-only connection_id
        with pytest.raises(ValueError, match="connection_id cannot be empty"):
            connections_namespace.sync(connection_id="   ")

    def test_sync_error_handling(self, connections_namespace, mock_client):
        """Test that sync() provides enhanced error handling."""
        # Test "not found" error enhancement
        mock_client.synchronize_cloud_storage_connection.side_effect = Exception(
            "Connection not found"
        )

        with pytest.raises(RuntimeError, match="Synchronization failed.*not found"):
            connections_namespace.sync(connection_id="conn_789")

        # Test "permission" error enhancement
        mock_client.synchronize_cloud_storage_connection.side_effect = Exception(
            "Access denied: insufficient permissions"
        )

        with pytest.raises(RuntimeError, match="Synchronization failed.*permissions"):
            connections_namespace.sync(connection_id="conn_789")

        # Test "connectivity" error enhancement
        mock_client.synchronize_cloud_storage_connection.side_effect = Exception(
            "Network connectivity issues"
        )

        with pytest.raises(RuntimeError, match="Synchronization failed.*connectivity"):
            connections_namespace.sync(connection_id="conn_789")

    def test_repr_functionality(self, connections_namespace):
        """Test string representation."""
        repr_str = repr(connections_namespace)
        assert "ConnectionsNamespace" in repr_str
