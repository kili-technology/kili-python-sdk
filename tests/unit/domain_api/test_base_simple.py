"""Simplified tests for the DomainNamespace base class."""

import gc
from unittest.mock import Mock

import pytest

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.domain_api.base import DomainNamespace


class MockDomainNamespace(DomainNamespace):
    """Test implementation of DomainNamespace for testing purposes."""

    __slots__ = ("_test_operation_count",)

    def __init__(self, client, gateway, domain_name=None):
        super().__init__(client, gateway, domain_name)
        self._test_operation_count = 0

    def test_operation(self):
        """Test operation that increments a counter."""
        self._test_operation_count += 1
        return self._test_operation_count


class TestDomainNamespaceSimple:
    """Simple functionality tests for DomainNamespace."""

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
    def domain_namespace(self, mock_client, mock_gateway):
        """Create a test DomainNamespace instance."""
        return MockDomainNamespace(mock_client, mock_gateway, "test_domain")

    def test_basic_initialization(self, domain_namespace, mock_client, mock_gateway):
        """Test basic namespace initialization."""
        assert domain_namespace.client is mock_client
        assert domain_namespace.gateway is mock_gateway
        assert domain_namespace.domain_name == "test_domain"

    def test_domain_name_defaults_to_class_name(self, mock_client, mock_gateway):
        """Test that domain name defaults to lowercase class name."""
        namespace = MockDomainNamespace(mock_client, mock_gateway)
        assert namespace.domain_name == "mockdomainnamespace"

    def test_custom_domain_name(self, mock_client, mock_gateway):
        """Test setting a custom domain name."""
        namespace = MockDomainNamespace(mock_client, mock_gateway, "custom_name")
        assert namespace.domain_name == "custom_name"

    def test_weak_reference_behavior(self):
        """Test weak reference behavior for client."""
        mock_client = Mock()
        mock_client.__class__.__name__ = "Kili"
        mock_gateway = Mock(spec=KiliAPIGateway)

        namespace = MockDomainNamespace(mock_client, mock_gateway)

        # Client should be accessible
        assert namespace.client is mock_client

        # Delete client reference
        del mock_client
        gc.collect()

        # Should raise ReferenceError when trying to access client
        with pytest.raises(ReferenceError):
            _ = namespace.client

    def test_refresh_functionality(self, domain_namespace):
        """Test basic refresh functionality."""
        # Should not raise any errors
        domain_namespace.refresh()

    def test_repr_functionality(self, domain_namespace):
        """Test string representation."""
        repr_str = repr(domain_namespace)
        assert "MockDomainNamespace" in repr_str
        assert "test_domain" in repr_str

    def test_basic_operation(self, domain_namespace):
        """Test basic operation execution."""
        result = domain_namespace.test_operation()
        assert result == 1

        result = domain_namespace.test_operation()
        assert result == 2
