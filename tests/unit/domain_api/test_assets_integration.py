"""Integration tests for AssetsNamespace with Kili client."""

from unittest.mock import MagicMock, patch

import pytest

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.client_domain import Kili


class TestAssetsNamespaceIntegration:
    """Integration tests for AssetsNamespace with the Kili client."""

    @pytest.fixture()
    def mock_graphql_client(self):
        """Mock GraphQL client."""
        return MagicMock()

    @pytest.fixture()
    def mock_http_client(self):
        """Mock HTTP client."""
        return MagicMock()

    @pytest.fixture()
    def mock_kili_client(self, mock_graphql_client, mock_http_client):
        """Create a mock Kili client with proper structure."""
        with (
            patch("kili.client.GraphQLClient"),
            patch("kili.client.HttpClient"),
            patch("kili.client.KiliAPIGateway") as mock_gateway_class,
            patch("kili.client.ApiKeyUseCases"),
            patch("kili.client.is_api_key_valid"),
            patch.dict("os.environ", {"KILI_SDK_SKIP_CHECKS": "1"}),
        ):
            mock_gateway = MagicMock(spec=KiliAPIGateway)
            mock_gateway_class.return_value = mock_gateway
            mock_gateway.get_project.return_value = {
                "steps": [{"id": "step_1", "name": "Default"}],
                "workflowVersion": "V2",
            }

            client = Kili(api_key="fake_key")
            return client

    def test_workflow_operations_delegation(self, mock_kili_client):
        """Test that workflow operations properly delegate to legacy methods."""
        # Mock the legacy workflow methods on the legacy_client
        mock_kili_client.legacy_client.assign_assets_to_labelers = MagicMock(
            return_value=[{"id": "asset1"}]
        )
        mock_kili_client.legacy_client.send_back_to_queue = MagicMock(
            return_value={"id": "project_123", "asset_ids": ["asset1"]}
        )
        mock_kili_client.legacy_client.add_to_review = MagicMock(
            return_value={"id": "project_123", "asset_ids": ["asset1"]}
        )

        assets_ns = mock_kili_client.assets

        # Test assign
        result = assets_ns.assign(asset_ids=["asset1"], to_be_labeled_by_array=[["user1"]])
        assert result[0]["id"] == "asset1"
        mock_kili_client.legacy_client.assign_assets_to_labelers.assert_called_once()

        # Test invalidate
        result = assets_ns.invalidate(asset_ids=["asset1"])
        assert result["id"] == "project_123"
        mock_kili_client.legacy_client.send_back_to_queue.assert_called_once()

        # Test move_to_next_step
        result = assets_ns.move_to_next_step(asset_ids=["asset1"])
        assert result["id"] == "project_123"
        mock_kili_client.legacy_client.add_to_review.assert_called_once()

    def test_list_and_count_use_cases_integration(self, mock_kili_client):
        """Test that list and count operations delegate to legacy client methods."""
        assets_ns = mock_kili_client.assets

        # Mock legacy client methods on the legacy_client
        mock_kili_client.legacy_client.assets = MagicMock(return_value=[{"id": "asset1"}])
        mock_kili_client.legacy_client.count_assets = MagicMock(return_value=5)

        # Test list assets
        result = assets_ns.list(project_id="project_123")
        assert len(result) == 1
        assert result[0]["id"] == "asset1"

        # Test count assets
        count = assets_ns.count(project_id="project_123")
        assert count == 5

        # Verify legacy methods were called
        mock_kili_client.legacy_client.assets.assert_called()
        mock_kili_client.legacy_client.count_assets.assert_called()


if __name__ == "__main__":
    pytest.main([__file__])
