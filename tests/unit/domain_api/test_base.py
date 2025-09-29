"""Tests for the DomainNamespace base class.

This module contains tests for the DomainNamespace base class
including basic functionality, memory management, and performance tests.
"""

import gc
from functools import lru_cache
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

    @lru_cache(maxsize=128)
    def cached_operation(self, value):
        """Test cached operation for testing cache clearing."""
        return f"cached_{value}_{self._test_operation_count}"


class TestDomainNamespaceBasic:
    """Basic functionality tests for DomainNamespace."""

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

    def test_initialization(self, domain_namespace, mock_client, mock_gateway):
        """Test that DomainNamespace initializes correctly."""
        assert domain_namespace._client is mock_client
        assert domain_namespace._gateway is mock_gateway
        assert domain_namespace._domain_name == "test_domain"

    def test_domain_name_property(self, domain_namespace):
        """Test the domain_name property."""
        assert domain_namespace._domain_name == "test_domain"

    def test_gateway_property(self, domain_namespace, mock_gateway):
        """Test the gateway property."""
        assert domain_namespace._gateway is mock_gateway

    def test_repr(self, domain_namespace):
        """Test the string representation."""
        repr_str = repr(domain_namespace)
        assert "MockDomainNamespace" in repr_str
        assert "client=Kili" in repr_str
        assert "domain='test_domain'" in repr_str

    def test_repr_with_garbage_collected_client(self, mock_gateway):
        """Test repr when client is garbage collected."""
        client = Mock()
        client.__class__.__name__ = "Kili"
        namespace = MockDomainNamespace(client, mock_gateway)

        # Delete client and force garbage collection
        del client
        gc.collect()

        repr_str = repr(namespace)
        assert "garbage collected" in repr_str


class TestDomainNamespaceCaching:
    """Tests for caching functionality."""

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

    def test_lru_cache_functionality(self, domain_namespace):
        """Test that LRU cache works correctly."""
        # Call cached operation multiple times with same value
        result1 = domain_namespace.cached_operation("test")
        result2 = domain_namespace.cached_operation("test")

        # Should return the same cached result
        assert result1 == result2

        # Different value should give different result
        result3 = domain_namespace.cached_operation("different")
        assert result3 != result1


class TestDomainNamespaceMemoryManagement:
    """Tests for memory management and performance."""

    def test_slots_memory_efficiency(self):
        """Test that __slots__ prevents dynamic attribute creation."""
        client = Mock()
        client.__class__.__name__ = "Kili"
        gateway = Mock(spec=KiliAPIGateway)

        namespace = DomainNamespace(client, gateway)

        # Should not be able to add arbitrary attributes
        with pytest.raises(AttributeError):
            namespace.arbitrary_attribute = "test"  # pyright: ignore[reportGeneralTypeIssues]

    def test_weak_reference_prevents_circular_refs(self):
        """Test that weak references prevent circular reference issues."""
        client = Mock()
        client.__class__.__name__ = "Kili"
        gateway = Mock(spec=KiliAPIGateway)

        # Create namespace
        namespace = DomainNamespace(client, gateway)

        # Create a circular reference scenario
        client.namespace = namespace

        # Get initial reference count
        client_refs = len(gc.get_referrers(client))

        # Delete namespace reference
        del namespace
        gc.collect()

        # Client should still be accessible and reference count should be reasonable
        assert client is not None
        new_client_refs = len(gc.get_referrers(client))

        # Reference count should not have increased significantly
        assert new_client_refs <= client_refs + 1
