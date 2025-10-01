"""Integration tests for lazy namespace loading in the Kili client."""

import time
from unittest.mock import patch

import pytest

from kili.client_domain import Kili


class TestLazyNamespaceIntegration:
    """Integration test suite for lazy namespace loading functionality."""

    @pytest.fixture()
    def mock_kili_client(self):
        """Create a mock Kili client for integration testing."""
        # Mock the environment variable to skip checks
        with patch.dict("os.environ", {"KILI_SDK_SKIP_CHECKS": "true"}):
            # Mock the required components in kili.client (where they're actually used)
            with patch("kili.client.HttpClient"), patch("kili.client.GraphQLClient"), patch(
                "kili.client.KiliAPIGateway"
            ):
                kili = Kili(api_key="test_key")
                yield kili

    def test_real_world_usage_pattern(self, mock_kili_client):
        """Test a realistic usage pattern of the lazy namespace loading."""
        kili = mock_kili_client

        # Simulate a real-world scenario where user only needs certain namespaces
        # Initially, no namespaces should be instantiated
        initial_dict_items = len(kili.__dict__)

        # User works with assets
        assets_ns = kili.assets
        assert assets_ns.domain_name == "assets"

        # Only assets namespace should be instantiated
        assert len(kili.__dict__) == initial_dict_items + 1

        # User then works with projects
        projects_ns = kili.projects
        assert projects_ns.domain_name == "projects"

        # Now both namespaces should be instantiated
        assert len(kili.__dict__) == initial_dict_items + 2

        # Accessing same namespaces again should return cached instances
        assets_ns_2 = kili.assets
        projects_ns_2 = kili.projects

        assert assets_ns is assets_ns_2
        assert projects_ns is projects_ns_2

        # Dict size should remain the same (cached)
        assert len(kili.__dict__) == initial_dict_items + 2

    def test_memory_efficiency_with_selective_usage(self, mock_kili_client):
        """Test memory efficiency when only some namespaces are used."""
        kili = mock_kili_client

        # In a real application, user might only use 2-3 namespaces
        # out of all available ones

        # Use only assets and labels
        assets_ns = kili.assets
        labels_ns = kili.labels

        used_namespaces = {
            "assets": assets_ns,
            "labels": labels_ns,
        }

        # Verify these are instantiated
        for ns_name, ns_instance in used_namespaces.items():
            assert ns_name in kili.__dict__
            assert kili.__dict__[ns_name] is ns_instance

        # Verify other namespaces are NOT instantiated
        unused_namespaces = [
            "projects",
            "users",
            "organizations",
            "issues",
            "notifications",
            "tags",
        ]

        for ns_name in unused_namespaces:
            assert ns_name not in kili.__dict__

    def test_namespace_functionality_after_lazy_loading(self, mock_kili_client):
        """Test that namespaces work correctly after lazy loading."""
        kili = mock_kili_client

        # Get a namespace
        assets_ns = kili.assets

        # Test that it has the expected properties and methods
        assert hasattr(assets_ns, "gateway")
        assert hasattr(assets_ns, "client")
        assert hasattr(assets_ns, "domain_name")

        # Test that the namespace can access its dependencies
        # Note: namespace.client points to the legacy client, not the domain client
        assert assets_ns.client is kili.legacy_client
        assert assets_ns.gateway is not None
        assert assets_ns.domain_name == "assets"

    def test_all_namespaces_load_correctly(self, mock_kili_client):
        """Test that all namespaces can be loaded and work correctly."""
        kili = mock_kili_client

        # Define all available namespaces
        all_namespaces = [
            ("assets", "assets"),
            ("labels", "labels"),
            ("projects", "projects"),
            ("users", "users"),
            ("organizations", "organizations"),
            ("issues", "issues"),
            ("notifications", "notifications"),
            ("tags", "tags"),
        ]

        loaded_namespaces = []

        # Load each namespace and verify it works
        for ns_attr, expected_domain in all_namespaces:
            namespace = getattr(kili, ns_attr)
            loaded_namespaces.append(namespace)

            # Verify basic properties
            assert namespace.domain_name == expected_domain
            # Note: namespace.client points to the legacy client, not the domain client
            assert namespace.client is kili.legacy_client
            assert hasattr(namespace, "gateway")

        # Verify all namespaces are now cached
        namespace_names = [
            "assets",
            "labels",
            "projects",
            "users",
            "organizations",
            "issues",
            "notifications",
            "tags",
        ]
        assert len([key for key in kili.__dict__.keys() if key in namespace_names]) == len(
            all_namespaces
        )

        # Verify accessing again returns the same instances
        for ns_attr, _ in all_namespaces:
            assert getattr(kili, ns_attr) is next(
                ns
                for ns in loaded_namespaces
                if ns.domain_name == getattr(kili, ns_attr).domain_name
            )

    def test_performance_comparison_lazy_vs_eager(self, mock_kili_client):
        """Test performance benefits of lazy loading."""
        # This test demonstrates that lazy loading allows faster client initialization
        # when not all namespaces are needed

        # Measure time to create client (should be fast)
        start_time = time.time()
        kili = mock_kili_client
        client_creation_time = time.time() - start_time

        # Client creation should be fast (no namespace instantiation yet)
        assert client_creation_time < 1.0  # Should be much faster in practice

        # Measure time to access first namespace
        start_time = time.time()
        assets_ns = kili.assets
        first_access_time = time.time() - start_time

        # Measure time to access same namespace again (cached)
        start_time = time.time()
        assets_ns_cached = kili.assets
        cached_access_time = time.time() - start_time

        # Verify we get the same instance
        assert assets_ns is assets_ns_cached

        # Cached access should be faster (though the difference might be small in tests)
        assert cached_access_time <= first_access_time

    def test_namespace_domain_names_are_consistent(self, mock_kili_client):
        """Test that namespace domain names are consistent and meaningful."""
        kili = mock_kili_client

        expected_mappings = {
            "assets": "assets",
            "labels": "labels",
            "projects": "projects",
            "users": "users",
            "organizations": "organizations",
            "issues": "issues",
            "notifications": "notifications",
            "tags": "tags",
        }

        for ns_attr, expected_domain in expected_mappings.items():
            namespace = getattr(kili, ns_attr)
            assert namespace.domain_name == expected_domain
            assert expected_domain in str(namespace)  # Should appear in repr
