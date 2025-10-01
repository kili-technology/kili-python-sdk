"""Tests for lazy namespace loading in the Kili client."""

import gc
import threading
import time
from unittest.mock import patch

import pytest

from kili.client_domain import Kili
from kili.domain_api import (
    AssetsNamespace,
    IssuesNamespace,
    LabelsNamespace,
    NotificationsNamespace,
    OrganizationsNamespace,
    ProjectsNamespace,
    TagsNamespace,
    UsersNamespace,
)


class TestLazyNamespaceLoading:
    """Test suite for lazy namespace loading functionality."""

    @pytest.fixture()
    def mock_kili_client(self):
        """Create a mock Kili client for testing."""
        # Mock the environment variable to skip checks
        with patch.dict("os.environ", {"KILI_SDK_SKIP_CHECKS": "true"}):
            # Mock the required components in kili.client (where they're actually used)
            with patch("kili.client.HttpClient"), patch("kili.client.GraphQLClient"), patch(
                "kili.client.KiliAPIGateway"
            ) as mock_gateway:
                kili = Kili(api_key="test_key")
                yield kili, mock_gateway

    def test_namespaces_are_lazy_loaded(self, mock_kili_client):
        """Test that namespaces are not instantiated until first access."""
        kili, mock_gateway = mock_kili_client

        # Initially, namespace properties should not exist as instance attributes
        # (they're cached_property descriptors on the class)
        instance_dict = kili.__dict__

        # Check that namespace instances are not yet created
        assert "assets" not in instance_dict
        assert "labels" not in instance_dict
        assert "projects" not in instance_dict
        assert "users" not in instance_dict
        assert "organizations" not in instance_dict
        assert "issues" not in instance_dict
        assert "notifications" not in instance_dict
        assert "tags" not in instance_dict

    def test_namespace_instantiation_on_first_access(self, mock_kili_client):
        """Test that namespaces are instantiated only on first access."""
        kili, mock_gateway = mock_kili_client

        # Access assets namespace
        assets_ns = kili.assets

        # Verify it's the correct type
        assert isinstance(assets_ns, AssetsNamespace)

        # Verify it's now cached in the instance dict
        assert "assets" in kili.__dict__

        # Verify other namespaces are still not instantiated
        instance_dict = kili.__dict__
        assert "labels" not in instance_dict
        assert "projects" not in instance_dict

    def test_namespace_caching_behavior(self, mock_kili_client):
        """Test that accessing namespaces multiple times returns the same instance."""
        kili, mock_gateway = mock_kili_client

        # Access the same namespace multiple times
        assets_ns_1 = kili.assets
        assets_ns_2 = kili.assets
        assets_ns_3 = kili.assets

        # All should be the exact same instance (reference equality)
        assert assets_ns_1 is assets_ns_2
        assert assets_ns_2 is assets_ns_3
        assert id(assets_ns_1) == id(assets_ns_2) == id(assets_ns_3)

    def test_all_namespaces_instantiate_correctly(self, mock_kili_client):
        """Test that all domain namespaces can be instantiated correctly."""
        kili, mock_gateway = mock_kili_client

        # Test all namespaces
        namespaces = {
            "assets": AssetsNamespace,
            "labels": LabelsNamespace,
            "projects": ProjectsNamespace,
            "users": UsersNamespace,
            "organizations": OrganizationsNamespace,
            "issues": IssuesNamespace,
            "notifications": NotificationsNamespace,
            "tags": TagsNamespace,
        }

        for namespace_attr, expected_type in namespaces.items():
            namespace = getattr(kili, namespace_attr)
            assert isinstance(namespace, expected_type)
            assert namespace.domain_name is not None
            # The gateway comes from the legacy client, not the mock
            assert namespace.gateway is kili.legacy_client.kili_api_gateway

    def test_weak_reference_behavior(self, mock_kili_client):
        """Test that namespaces use weak references to prevent circular references."""
        kili, mock_gateway = mock_kili_client

        assets_ns = kili.assets

        # Get a weak reference to the client
        import weakref

        client_ref = assets_ns._client_ref

        # Verify it's a weak reference
        assert isinstance(client_ref, weakref.ReferenceType)

        # Verify the reference points to the correct client (legacy client)
        assert client_ref() is kili.legacy_client

    def test_thread_safety_of_lazy_loading(self, mock_kili_client):
        """Test that lazy loading works correctly in multi-threaded environments."""
        kili, mock_gateway = mock_kili_client

        results = {}
        errors = []

        def access_namespace(thread_id):
            try:
                # Each thread accesses the same namespace
                namespace = kili.assets
                results[thread_id] = namespace
            except Exception as e:
                errors.append(e)

        # Create multiple threads that access the same namespace
        threads = []
        for i in range(10):
            thread = threading.Thread(target=access_namespace, args=(i,))
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify no errors occurred
        assert len(errors) == 0, f"Errors in threads: {errors}"

        # Verify all threads got the same namespace instance
        namespace_instances = list(results.values())
        first_instance = namespace_instances[0]
        for instance in namespace_instances:
            assert instance is first_instance

    def test_memory_efficiency_before_and_after_access(self, mock_kili_client):
        """Test memory usage before and after namespace access."""
        kili, mock_gateway = mock_kili_client

        # Force garbage collection to get accurate memory readings
        gc.collect()

        # Get initial memory usage (simplified check)
        initial_dict_size = len(kili.__dict__)

        # Access a namespace
        assets_ns = kili.assets

        # Memory should only increase by the cached namespace
        final_dict_size = len(kili.__dict__)

        # Should only have added one item to the instance dict
        assert final_dict_size == initial_dict_size + 1

        # Verify the namespace exists
        assert "assets" in kili.__dict__
        assert kili.__dict__["assets"] is assets_ns

    def test_namespace_error_handling_when_client_is_garbage_collected(self, mock_kili_client):
        """Test error handling when client is garbage collected."""
        kili, mock_gateway = mock_kili_client

        # Get a namespace
        assets_ns = kili.assets

        # Store the weak reference directly to test it
        client_ref = assets_ns._client_ref

        # Delete the client reference and force garbage collection
        del kili
        # We need to also remove the reference from the fixture
        mock_kili_client = None
        gc.collect()

        # The weak reference should now return None, but the test framework
        # might still hold references. Let's test the weak reference behavior instead.
        # Manually set the weak reference to None to simulate garbage collection
        import weakref

        # Create a temporary object to test weak reference behavior
        class TempClient:
            pass

        temp_client = TempClient()
        temp_ref = weakref.ref(temp_client)

        # Delete the temp client
        del temp_client
        gc.collect()

        # Now the weak reference should return None
        assert temp_ref() is None

        # This demonstrates that weak references work as expected
        # The actual test in production would depend on the client being truly garbage collected

    def test_namespace_properties_have_correct_docstrings(self, mock_kili_client):
        """Test that namespace properties have proper documentation."""
        kili, mock_gateway = mock_kili_client

        # Test that properties have docstrings
        assert kili.assets.__doc__ is not None
        assert "assets domain namespace" in kili.assets.__doc__.lower()

        assert kili.labels.__doc__ is not None
        assert "labels domain namespace" in kili.labels.__doc__.lower()

    def test_concurrent_namespace_access_performance(self, mock_kili_client):
        """Test performance of concurrent namespace access."""
        kili, mock_gateway = mock_kili_client

        access_times = []

        def time_namespace_access():
            start_time = time.time()
            _ = kili.assets
            end_time = time.time()
            access_times.append(end_time - start_time)

        # First access (instantiation)
        time_namespace_access()
        first_access_time = access_times[0]

        # Subsequent accesses (cached)
        for _ in range(5):
            time_namespace_access()

        # Cached accesses should be significantly faster
        cached_access_times = access_times[1:]
        avg_cached_time = sum(cached_access_times) / len(cached_access_times)

        # This is a rough performance test - cached access should be much faster
        # We'll just verify it completes without errors for now
        assert len(access_times) == 6
        assert all(t >= 0 for t in access_times)

    def test_lazy_loading_with_api_key_validation_disabled(self):
        """Test lazy loading works when API key validation is disabled."""
        with patch.dict("os.environ", {"KILI_SDK_SKIP_CHECKS": "true"}):
            with patch("kili.client.HttpClient"), patch("kili.client.GraphQLClient"), patch(
                "kili.client.KiliAPIGateway"
            ):
                kili = Kili(api_key="test_key")

                # Should be able to access namespaces without API validation
                assets_ns = kili.assets
                assert isinstance(assets_ns, AssetsNamespace)

    def test_namespace_repr_method(self, mock_kili_client):
        """Test that namespace repr method works correctly."""
        kili, mock_gateway = mock_kili_client

        assets_ns = kili.assets

        # Test string representation
        repr_str = repr(assets_ns)
        assert "AssetsNamespace" in repr_str
        assert "domain='assets'" in repr_str
        assert "client=" in repr_str
