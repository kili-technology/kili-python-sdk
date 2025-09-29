"""Simplified tests for the DomainNamespace base class."""

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
        assert domain_namespace._client is mock_client
        assert domain_namespace._gateway is mock_gateway
        assert domain_namespace._domain_name == "test_domain"

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
