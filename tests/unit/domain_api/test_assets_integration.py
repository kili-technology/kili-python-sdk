"""Integration tests for AssetsNamespace with Kili client."""

from unittest.mock import MagicMock, patch

import pytest

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.client_domain import Kili
from kili.domain_api.assets import AssetsNamespace


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
        with patch("kili.client.GraphQLClient"), patch("kili.client.HttpClient"), patch(
            "kili.client.KiliAPIGateway"
        ) as mock_gateway_class, patch("kili.client.ApiKeyUseCases"), patch(
            "kili.client.is_api_key_valid"
        ), patch.dict("os.environ", {"KILI_SDK_SKIP_CHECKS": "1"}):
            mock_gateway = MagicMock(spec=KiliAPIGateway)
            mock_gateway_class.return_value = mock_gateway
            mock_gateway.get_project.return_value = {
                "steps": [{"id": "step_1", "name": "Default"}],
                "workflowVersion": "V2",
            }

            client = Kili(api_key="fake_key")
            return client

    def test_assets_namespace_lazy_loading(self, mock_kili_client):
        """Test that assets is lazily loaded and cached."""
        # First access should create the namespace
        assets_ns1 = mock_kili_client.assets
        assert isinstance(assets_ns1, AssetsNamespace)

        # Second access should return the same instance (cached)
        assets_ns2 = mock_kili_client.assets
        assert assets_ns1 is assets_ns2

    def test_nested_namespaces_available(self, mock_kili_client):
        """Test that nested namespaces are available."""
        assets_ns = mock_kili_client.assets

        # Check that all nested namespaces are available
        assert hasattr(assets_ns, "workflow")
        assert hasattr(assets_ns, "external_ids")
        assert hasattr(assets_ns, "metadata")

        # Check that workflow has step namespace
        assert hasattr(assets_ns.workflow, "step")

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

        # Test workflow assign
        result = assets_ns.workflow.assign(asset_ids=["asset1"], to_be_labeled_by_array=[["user1"]])
        assert result[0]["id"] == "asset1"
        mock_kili_client.legacy_client.assign_assets_to_labelers.assert_called_once()

        # Test workflow step invalidate
        result = assets_ns.workflow.step.invalidate(asset_ids=["asset1"])
        assert result["id"] == "project_123"
        mock_kili_client.legacy_client.send_back_to_queue.assert_called_once()

        # Test workflow step next
        result = assets_ns.workflow.step.next(asset_ids=["asset1"])
        assert result["id"] == "project_123"
        mock_kili_client.legacy_client.add_to_review.assert_called_once()

    def test_metadata_operations_delegation(self, mock_kili_client):
        """Test that metadata operations properly delegate to legacy methods."""
        # Mock the legacy metadata methods on the legacy_client
        mock_kili_client.legacy_client.add_metadata = MagicMock(return_value=[{"id": "asset1"}])
        mock_kili_client.legacy_client.set_metadata = MagicMock(return_value=[{"id": "asset1"}])

        assets_ns = mock_kili_client.assets

        # Test metadata add
        result = assets_ns.metadata.add(
            json_metadata=[{"key": "value"}], project_id="project_123", asset_ids=["asset1"]
        )
        assert result[0]["id"] == "asset1"
        mock_kili_client.legacy_client.add_metadata.assert_called_once()

        # Test metadata set
        result = assets_ns.metadata.set(
            json_metadata=[{"key": "value"}], project_id="project_123", asset_ids=["asset1"]
        )
        assert result[0]["id"] == "asset1"
        mock_kili_client.legacy_client.set_metadata.assert_called_once()

    def test_external_ids_operations_delegation(self, mock_kili_client):
        """Test that external IDs operations properly delegate to legacy methods."""
        # Mock the legacy external IDs method on the legacy_client
        mock_kili_client.legacy_client.change_asset_external_ids = MagicMock(
            return_value=[{"id": "asset1"}]
        )

        assets_ns = mock_kili_client.assets

        # Test external IDs update
        result = assets_ns.external_ids.update(new_external_ids=["new_ext1"], asset_ids=["asset1"])
        assert result[0]["id"] == "asset1"
        mock_kili_client.legacy_client.change_asset_external_ids.assert_called_once()

    @patch("kili.domain_api.assets.AssetUseCases")
    def test_list_and_count_use_cases_integration(self, mock_asset_use_cases, mock_kili_client):
        """Test that list and count operations use AssetUseCases properly."""
        mock_use_case_instance = MagicMock()
        mock_asset_use_cases.return_value = mock_use_case_instance

        # Mock use case methods
        mock_use_case_instance.list_assets.return_value = iter([{"id": "asset1"}])
        mock_use_case_instance.count_assets.return_value = 5

        assets_ns = mock_kili_client.assets

        # Test list assets
        result_gen = assets_ns.list(project_id="project_123")
        assets_list = list(result_gen)
        assert len(assets_list) == 1
        assert assets_list[0]["id"] == "asset1"

        # Test count assets
        count = assets_ns.count(project_id="project_123")
        assert count == 5

        # Verify AssetUseCases was created with correct gateway
        mock_asset_use_cases.assert_called_with(assets_ns.gateway)

    def test_namespace_inheritance(self, mock_kili_client):
        """Test that AssetsNamespace properly inherits from DomainNamespace."""
        assets_ns = mock_kili_client.assets

        # Test DomainNamespace properties
        assert hasattr(assets_ns, "client")
        assert hasattr(assets_ns, "gateway")
        assert hasattr(assets_ns, "domain_name")
        assert assets_ns.domain_name == "assets"


if __name__ == "__main__":
    pytest.main([__file__])
