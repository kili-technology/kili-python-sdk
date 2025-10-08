"""Test infrastructure validation for domain_v2 integration tests.

This test file validates that the testing infrastructure is set up correctly
and that basic patterns work as expected.
"""


from tests_v2 import assert_is_view, assert_view_has_dict_compatibility


def test_fixtures_available(kili_client, api_key, api_endpoint):
    """Test that all fixtures are available and configured correctly."""
    # Verify fixtures are provided
    assert kili_client is not None, "kili_client fixture should be available"
    assert api_key is not None, "api_key fixture should be available"
    assert api_endpoint is not None, "api_endpoint fixture should be available"

    # Verify API key format
    assert isinstance(api_key, str), "API key should be a string"
    assert len(api_key) > 0, "API key should not be empty"

    # Verify endpoint format
    assert isinstance(api_endpoint, str), "Endpoint should be a string"
    assert api_endpoint.startswith("http"), "Endpoint should be a URL"


def test_kili_client_structure(kili_client):
    """Test that kili_client has expected domain namespaces."""
    # Verify client has domain namespaces
    assert hasattr(kili_client, "assets"), "Client should have assets namespace"
    assert hasattr(kili_client, "labels"), "Client should have labels namespace"
    assert hasattr(kili_client, "projects"), "Client should have projects namespace"
    assert hasattr(kili_client, "users"), "Client should have users namespace"


def test_utility_functions_importable():
    """Test that utility functions are importable and callable."""
    # These imports should not raise
    from tests_v2 import (  # pylint: disable=import-outside-toplevel
        assert_is_view,
        assert_view_has_dict_compatibility,
        assert_view_property_access,
    )

    # Verify they are callable
    assert callable(assert_is_view)
    assert callable(assert_view_has_dict_compatibility)
    assert callable(assert_view_property_access)


def test_view_utilities_with_sample_data():
    """Test that View utilities work with sample data."""
    from kili.domain_v2.asset import (  # pylint: disable=import-outside-toplevel
        AssetContract,
        AssetView,
    )

    # Create sample data
    sample_data: AssetContract = {
        "id": "test-id-123",
        "externalId": "test-external-id",
        "content": "https://example.com/test.jpg",
        "labels": [],
        "isHoneypot": False,
        "skipped": False,
    }

    # Create View
    view = AssetView(sample_data)

    # Test utilities
    assert_is_view(view, AssetView)
    assert_view_has_dict_compatibility(view)

    # Verify basic properties
    assert view.id == "test-id-123"
    assert view.external_id == "test-external-id"
    assert view.display_name == "test-external-id"
