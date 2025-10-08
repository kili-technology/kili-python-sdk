"""Unit tests for IntegrationsNamespace."""

from unittest.mock import MagicMock, patch

import pytest

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.client_domain import Kili
from kili.domain_api.integrations import IntegrationsNamespace
from kili.domain_v2.integration import IntegrationView


class TestIntegrationsNamespace:
    """Unit tests for IntegrationsNamespace."""

    @pytest.fixture()
    def mock_kili_client(self):
        """Create a mock Kili client with proper structure."""
        with patch("kili.client.GraphQLClient"), patch("kili.client.HttpClient"), patch(
            "kili.client.KiliAPIGateway"
        ) as mock_gateway_class, patch("kili.client.ApiKeyUseCases"), patch(
            "kili.client.is_api_key_valid"
        ), patch.dict("os.environ", {"KILI_SDK_SKIP_CHECKS": "1"}):
            mock_gateway = MagicMock(spec=KiliAPIGateway)
            mock_gateway_class.return_value = mock_gateway

            client = Kili(api_key="fake_key")
            return client

    def test_integrations_namespace_lazy_loading(self, mock_kili_client):
        """Test that integrations namespace is lazily loaded and cached."""
        # First access should create the namespace
        integrations_ns1 = mock_kili_client.integrations
        assert isinstance(integrations_ns1, IntegrationsNamespace)

        # Second access should return the same instance (cached)
        integrations_ns2 = mock_kili_client.integrations
        assert integrations_ns1 is integrations_ns2

    @patch("kili.domain_api.integrations.CloudStorageClientMethods")
    def test_create_returns_integration_view(self, mock_cloud_storage_methods, mock_kili_client):
        """Test that create() returns an IntegrationView object."""
        # Mock the legacy method to return a dict (with camelCase fields as returned by API)
        mock_cloud_storage_methods.create_cloud_storage_integration.return_value = {
            "id": "integration_123",
            "name": "Test Integration",
            "platform": "AWS",
            "status": "CONNECTED",
            "organizationId": "org_456",
        }

        integrations_ns = mock_kili_client.integrations

        # Call create
        result = integrations_ns.create(
            platform="AWS",
            name="Test Integration",
            s3_bucket_name="test-bucket",
            s3_region="us-east-1",
            s3_access_key="AKIAIOSFODNN7EXAMPLE",
            s3_secret_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        )

        # Verify result is an IntegrationView
        assert isinstance(result, IntegrationView)
        assert result.id == "integration_123"
        assert result.name == "Test Integration"
        assert result.platform == "AWS"
        assert result.status == "CONNECTED"
        assert result.organization_id == "org_456"

        # Verify the legacy method was called
        mock_cloud_storage_methods.create_cloud_storage_integration.assert_called_once()

    @patch("kili.domain_api.integrations.CloudStorageClientMethods")
    def test_update_returns_integration_view(self, mock_cloud_storage_methods, mock_kili_client):
        """Test that update() returns an IntegrationView object."""
        # Mock the legacy method to return a dict (with camelCase fields as returned by API)
        mock_cloud_storage_methods.update_cloud_storage_integration.return_value = {
            "id": "integration_123",
            "name": "Updated Integration",
            "platform": "AWS",
            "status": "CONNECTED",
            "organizationId": "org_456",
        }

        integrations_ns = mock_kili_client.integrations

        # Call update
        result = integrations_ns.update(
            integration_id="integration_123",
            name="Updated Integration",
            allowed_paths=["/data/training", "/data/validation"],
        )

        # Verify result is an IntegrationView
        assert isinstance(result, IntegrationView)
        assert result.id == "integration_123"
        assert result.name == "Updated Integration"
        assert result.platform == "AWS"
        assert result.status == "CONNECTED"
        assert result.organization_id == "org_456"

        # Verify the legacy method was called
        mock_cloud_storage_methods.update_cloud_storage_integration.assert_called_once()

    @patch("kili.domain_api.integrations.CloudStorageClientMethods")
    def test_list_returns_integration_views(self, mock_cloud_storage_methods, mock_kili_client):
        """Test that list() returns IntegrationView objects."""
        # Mock the legacy method to return a list of dicts (with camelCase fields as returned by API)
        mock_cloud_storage_methods.cloud_storage_integrations.return_value = [
            {
                "id": "integration_1",
                "name": "Integration 1",
                "platform": "AWS",
                "status": "CONNECTED",
                "organizationId": "org_123",
            },
            {
                "id": "integration_2",
                "name": "Integration 2",
                "platform": "AZURE",
                "status": "CONNECTED",
                "organizationId": "org_123",
            },
        ]

        integrations_ns = mock_kili_client.integrations

        # Call list
        result = integrations_ns.list(as_generator=False)

        # Verify result is a list of IntegrationView objects
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(item, IntegrationView) for item in result)
        assert result[0].id == "integration_1"
        assert result[0].platform == "AWS"
        assert result[1].id == "integration_2"
        assert result[1].platform == "AZURE"

        # Verify the legacy method was called
        mock_cloud_storage_methods.cloud_storage_integrations.assert_called_once()

    def test_namespace_inheritance(self, mock_kili_client):
        """Test that IntegrationsNamespace properly inherits from DomainNamespace."""
        integrations_ns = mock_kili_client.integrations

        # Test DomainNamespace properties
        assert hasattr(integrations_ns, "client")
        assert hasattr(integrations_ns, "gateway")
        assert hasattr(integrations_ns, "domain_name")
        assert integrations_ns.domain_name == "integrations"


if __name__ == "__main__":
    pytest.main([__file__])
