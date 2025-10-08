"""Integration tests for IntegrationView objects returned by the integrations namespace.

This test file validates that the integrations.list() method correctly returns
IntegrationView objects instead of dictionaries, and that these objects provide
proper property access and backward compatibility.

Test Strategy:
    - Verify list() returns IntegrationView objects in all modes (list, generator)
    - Test IntegrationView property access for common properties
    - Validate backward compatibility with dictionary interface via to_dict()
    - Test filtering by platform and status
    - Verify computed properties (is_connected, is_checking, has_error, is_active)
    - Ensure mutation methods still return dicts (unchanged)
"""

import pytest

from kili.domain_v2.integration import IntegrationView
from tests_v2 import (
    assert_is_view,
    assert_view_has_dict_compatibility,
    assert_view_property_access,
)


@pytest.mark.integration()
def test_list_returns_integration_views(kili_client):
    """Test that integrations.list() in list mode returns IntegrationView objects."""
    # Get integrations in list mode
    integrations = kili_client.integrations.list(first=5, as_generator=False)

    # Verify we get a list
    assert isinstance(
        integrations, list
    ), "integrations.list() with as_generator=False should return a list"

    # Skip if no integrations
    if not integrations:
        pytest.skip("No integrations available for testing")

    # Verify each item is an IntegrationView
    for integration in integrations:
        assert_is_view(integration, IntegrationView)

        # Verify we can access basic properties
        assert hasattr(integration, "id")
        assert hasattr(integration, "name")
        assert hasattr(integration, "platform")
        assert hasattr(integration, "status")
        assert hasattr(integration, "organization_id")


@pytest.mark.integration()
def test_list_generator_returns_integration_views(kili_client):
    """Test that integrations.list() in generator mode returns IntegrationView objects."""
    # Get integrations in generator mode
    integrations_gen = kili_client.integrations.list(first=5, as_generator=True)

    # Take first 5 items from generator (or fewer if less available)
    integrations_from_gen = []
    for i, integration in enumerate(integrations_gen):
        if i >= 5:
            break
        integrations_from_gen.append(integration)

    # Skip if no integrations
    if not integrations_from_gen:
        pytest.skip("No integrations available for testing")

    # Verify each yielded item is an IntegrationView
    for integration in integrations_from_gen:
        assert_is_view(integration, IntegrationView)

        # Verify we can access basic properties
        assert hasattr(integration, "id")
        assert hasattr(integration, "name")
        assert hasattr(integration, "platform")
        assert hasattr(integration, "status")


@pytest.mark.integration()
def test_integration_view_properties(kili_client):
    """Test that IntegrationView provides access to all expected properties."""
    # Get first integration
    integrations = kili_client.integrations.list(first=1, as_generator=False)

    if not integrations:
        pytest.skip("No integrations available for testing")

    integration = integrations[0]

    # Verify IntegrationView type
    assert_is_view(integration, IntegrationView)

    # Test core properties exist and are accessible
    assert_view_property_access(integration, "id")
    assert_view_property_access(integration, "name")
    assert_view_property_access(integration, "platform")
    assert_view_property_access(integration, "status")
    assert_view_property_access(integration, "organization_id")

    # Test that id is not empty
    assert integration.id, "Integration id should not be empty"

    # Test that name is not empty
    assert integration.name, "Integration name should not be empty"

    # Test that platform is valid
    assert integration.platform in [
        "AWS",
        "AZURE",
        "GCP",
        "S3",
        None,
    ], "platform should be one of AWS, AZURE, GCP, S3, or None"

    # Test that status is valid
    assert integration.status in [
        "CONNECTED",
        "CHECKING",
        "ERROR",
        None,
    ], "status should be one of CONNECTED, CHECKING, ERROR, or None"

    # Test computed properties
    assert_view_property_access(integration, "is_connected")
    assert_view_property_access(integration, "is_checking")
    assert_view_property_access(integration, "has_error")
    assert_view_property_access(integration, "is_active")
    assert_view_property_access(integration, "display_name")

    # Test that exactly one status property is True
    status_properties = [integration.is_connected, integration.is_checking, integration.has_error]
    # At most one should be True (or none if status is None)
    assert (
        sum(status_properties) <= 1
    ), "At most one of is_connected, is_checking, has_error should be True"

    # Test that is_active is an alias for is_connected
    assert (
        integration.is_active == integration.is_connected
    ), "is_active should be an alias for is_connected"

    # Test display_name (should be name or id)
    assert integration.display_name, "display_name should not be empty"
    if integration.name:
        assert integration.display_name == integration.name
    else:
        assert integration.display_name == integration.id


@pytest.mark.integration()
def test_integration_view_dict_compatibility(kili_client):
    """Test that IntegrationView maintains backward compatibility via to_dict()."""
    # Get first integration
    integrations = kili_client.integrations.list(first=1, as_generator=False)

    if not integrations:
        pytest.skip("No integrations available for testing")

    integration = integrations[0]

    # Verify IntegrationView type
    assert_is_view(integration, IntegrationView)

    # Test dictionary compatibility
    assert_view_has_dict_compatibility(integration)

    # Get dictionary representation
    integration_dict = integration.to_dict()

    # Verify it's a dictionary
    assert isinstance(integration_dict, dict), "to_dict() should return a dictionary"

    # Verify dictionary has expected keys
    assert "id" in integration_dict, "Dictionary should have 'id' key"

    # Verify dictionary values match property values
    if "name" in integration_dict:
        assert integration_dict["name"] == integration.name, "Dictionary name should match property"

    if "platform" in integration_dict:
        assert (
            integration_dict["platform"] == integration.platform
        ), "Dictionary platform should match property"

    if "status" in integration_dict:
        assert (
            integration_dict["status"] == integration.status
        ), "Dictionary status should match property"

    if "organizationId" in integration_dict:
        assert (
            integration_dict["organizationId"] == integration.organization_id
        ), "Dictionary organizationId should match property"

    # Verify to_dict() returns the same reference (zero-copy)
    assert (
        integration_dict is integration._data
    ), "to_dict() should return the same reference as _data"


@pytest.mark.integration()
def test_integration_view_filtering(kili_client):
    """Test that IntegrationView objects work correctly with filtering."""
    # Get all integrations
    all_integrations = kili_client.integrations.list(first=10, as_generator=False)

    if not all_integrations:
        pytest.skip("No integrations available for testing")

    # Get the first integration's platform and status for filtering
    first_integration = all_integrations[0]

    # Test filtering by platform (if platform is set)
    if first_integration.platform:
        platform_integrations = kili_client.integrations.list(
            platform=first_integration.platform, first=10, as_generator=False
        )

        # Verify results are IntegrationView objects
        for integration in platform_integrations:
            assert_is_view(integration, IntegrationView)
            # All should have the same platform
            assert (
                integration.platform == first_integration.platform
            ), "Filtered integrations should have the specified platform"

    # Test filtering by status (if status is set)
    if first_integration.status:
        status_integrations = kili_client.integrations.list(
            status=first_integration.status, first=10, as_generator=False
        )

        # Verify results are IntegrationView objects
        for integration in status_integrations:
            assert_is_view(integration, IntegrationView)
            # All should have the same status
            assert (
                integration.status == first_integration.status
            ), "Filtered integrations should have the specified status"


@pytest.mark.integration()
def test_integration_view_empty_results(kili_client):
    """Test that empty results are handled correctly."""
    # Query all integrations - may or may not be empty
    # This tests that empty results return an empty list
    integrations = kili_client.integrations.list(as_generator=False)

    # Verify we get a list (even if empty)
    assert isinstance(integrations, list), "Should return a list even when no results"


@pytest.mark.integration()
def test_integration_view_status_properties(kili_client):
    """Test that status-related computed properties work correctly."""
    # Get all integrations
    integrations = kili_client.integrations.list(first=10, as_generator=False)

    if not integrations:
        pytest.skip("No integrations available for testing")

    for integration in integrations:
        # Verify IntegrationView type
        assert_is_view(integration, IntegrationView)

        # Test status properties based on the actual status
        if integration.status == "CONNECTED":
            assert integration.is_connected is True
            assert integration.is_checking is False
            assert integration.has_error is False
        elif integration.status == "CHECKING":
            assert integration.is_connected is False
            assert integration.is_checking is True
            assert integration.has_error is False
        elif integration.status == "ERROR":
            assert integration.is_connected is False
            assert integration.is_checking is False
            assert integration.has_error is True
        else:
            # Status is None or unexpected
            assert integration.is_connected is False
            assert integration.is_checking is False
            assert integration.has_error is False

        # Verify is_active is an alias for is_connected
        assert integration.is_active == integration.is_connected


@pytest.mark.integration()
def test_integration_view_with_fields_parameter(kili_client):
    """Test that IntegrationView works correctly with custom fields parameter."""
    # Query with specific fields
    integrations = kili_client.integrations.list(
        first=1, fields=["id", "name", "platform", "status", "organizationId"], as_generator=False
    )

    if not integrations:
        pytest.skip("No integrations available for testing")

    integration = integrations[0]

    # Verify it's still an IntegrationView
    assert_is_view(integration, IntegrationView)

    # Verify requested fields are accessible
    assert_view_property_access(integration, "id")
    assert_view_property_access(integration, "name")
    assert_view_property_access(integration, "platform")
    assert_view_property_access(integration, "status")
    assert_view_property_access(integration, "organization_id")


@pytest.mark.integration()
def test_integration_count_method(kili_client):
    """Test that integrations.count() works correctly and returns an integer."""
    # Count all integrations
    total_count = kili_client.integrations.count()

    # Verify result is an integer
    assert isinstance(total_count, int), "count() should return an integer"
    assert total_count >= 0, "count() should return a non-negative integer"

    # If there are integrations, test filtered counts
    if total_count > 0:
        # Get first integration to test filtered counts
        integrations = kili_client.integrations.list(first=1, as_generator=False)
        if integrations:
            first_integration = integrations[0]

            # Count by platform (if platform is set)
            if first_integration.platform:
                platform_count = kili_client.integrations.count(platform=first_integration.platform)
                assert isinstance(platform_count, int), "count() should return an integer"
                assert platform_count >= 1, "Should count at least the first integration"
                assert platform_count <= total_count, "Filtered count should not exceed total count"

            # Count by status (if status is set)
            if first_integration.status:
                status_count = kili_client.integrations.count(status=first_integration.status)
                assert isinstance(status_count, int), "count() should return an integer"
                assert status_count >= 1, "Should count at least the first integration"
                assert status_count <= total_count, "Filtered count should not exceed total count"


@pytest.mark.integration()
def test_integration_view_display_name(kili_client):
    """Test that display_name property works correctly."""
    # Get all integrations
    integrations = kili_client.integrations.list(first=5, as_generator=False)

    if not integrations:
        pytest.skip("No integrations available for testing")

    for integration in integrations:
        # Verify IntegrationView type
        assert_is_view(integration, IntegrationView)

        # Test display_name property
        assert_view_property_access(integration, "display_name")

        # Verify display_name logic
        if integration.name:
            assert (
                integration.display_name == integration.name
            ), "display_name should return name when name is set"
        else:
            assert (
                integration.display_name == integration.id
            ), "display_name should return id when name is not set"

        # Verify display_name is never empty
        assert integration.display_name, "display_name should not be empty"
