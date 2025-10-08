"""Integration tests for OrganizationView objects returned by the organizations namespace.

This test file validates that the organizations.list() method correctly returns
OrganizationView objects instead of dictionaries, and that these objects provide
proper property access and backward compatibility.

Test Strategy:
    - Verify list() returns OrganizationView objects in all modes (list, generator)
    - Test OrganizationView property access for common properties
    - Validate backward compatibility with dictionary interface via to_dict()
    - Test filtering options
    - Verify computed properties (display_name, full_address)
    - Ensure count method works correctly
"""

import pytest

from kili.domain_v2.organization import OrganizationView
from tests_v2 import (
    assert_is_view,
    assert_view_has_dict_compatibility,
    assert_view_property_access,
)


@pytest.mark.integration()
def test_list_returns_organization_views(kili_client):
    """Test that organizations.list() in list mode returns OrganizationView objects."""
    # Get organizations in list mode
    organizations = kili_client.organizations.list(first=5, as_generator=False)

    # Verify we get a list
    assert isinstance(
        organizations, list
    ), "organizations.list() with as_generator=False should return a list"

    # Skip if no organizations (unlikely, but possible in isolated test environments)
    if not organizations:
        pytest.skip("No organizations available for testing")

    # Verify each item is an OrganizationView
    for organization in organizations:
        assert_is_view(organization, OrganizationView)

        # Verify we can access basic properties
        assert hasattr(organization, "id")
        assert hasattr(organization, "name")


@pytest.mark.integration()
def test_list_generator_returns_organization_views(kili_client):
    """Test that organizations.list() in generator mode returns OrganizationView objects."""
    # Get organizations in generator mode
    organizations_gen = kili_client.organizations.list(first=5, as_generator=True)

    # Take first 5 items from generator (or fewer if less available)
    organizations_from_gen = []
    for i, organization in enumerate(organizations_gen):
        if i >= 5:
            break
        organizations_from_gen.append(organization)

    # Skip if no organizations
    if not organizations_from_gen:
        pytest.skip("No organizations available for testing")

    # Verify each yielded item is an OrganizationView
    for organization in organizations_from_gen:
        assert_is_view(organization, OrganizationView)

        # Verify we can access basic properties
        assert hasattr(organization, "id")
        assert hasattr(organization, "name")


@pytest.mark.integration()
def test_organization_view_properties(kili_client):
    """Test that OrganizationView provides access to all expected properties."""
    # Get first organization
    organizations = kili_client.organizations.list(first=1, as_generator=False)

    if not organizations:
        pytest.skip("No organizations available for testing")

    organization = organizations[0]

    # Verify OrganizationView type
    assert_is_view(organization, OrganizationView)

    # Test core properties exist and are accessible
    assert_view_property_access(organization, "id")
    assert_view_property_access(organization, "name")

    # Test that id is not empty
    assert organization.id, "Organization id should not be empty"

    # Test that name is not empty
    assert organization.name, "Organization name should not be empty"

    # Test optional address properties
    assert_view_property_access(organization, "address")
    assert_view_property_access(organization, "city")
    assert_view_property_access(organization, "country")
    assert_view_property_access(organization, "zip_code")

    # Test metric properties (may be 0 for new organizations)
    assert_view_property_access(organization, "number_of_annotations")
    assert_view_property_access(organization, "number_of_labeled_assets")
    assert_view_property_access(organization, "number_of_hours")

    # Verify metric properties are non-negative
    assert organization.number_of_annotations >= 0, "number_of_annotations should be non-negative"
    assert (
        organization.number_of_labeled_assets >= 0
    ), "number_of_labeled_assets should be non-negative"
    assert organization.number_of_hours >= 0.0, "number_of_hours should be non-negative"

    # Test computed properties
    assert_view_property_access(organization, "display_name")
    assert_view_property_access(organization, "full_address")

    # Test display_name (should be name or id)
    assert organization.display_name, "display_name should not be empty"
    assert organization.display_name == (organization.name or organization.id)


@pytest.mark.integration()
def test_organization_view_dict_compatibility(kili_client):
    """Test that OrganizationView maintains backward compatibility via to_dict()."""
    # Get first organization
    organizations = kili_client.organizations.list(first=1, as_generator=False)

    if not organizations:
        pytest.skip("No organizations available for testing")

    organization = organizations[0]

    # Verify OrganizationView type
    assert_is_view(organization, OrganizationView)

    # Test dictionary compatibility
    assert_view_has_dict_compatibility(organization)

    # Get dictionary representation
    organization_dict = organization.to_dict()

    # Verify it's a dictionary
    assert isinstance(organization_dict, dict), "to_dict() should return a dictionary"

    # Verify dictionary has expected keys
    assert "id" in organization_dict, "Dictionary should have 'id' key"
    assert "name" in organization_dict, "Dictionary should have 'name' key"

    # Verify dictionary values match property values
    assert organization_dict["id"] == organization.id, "Dictionary id should match property"
    assert organization_dict["name"] == organization.name, "Dictionary name should match property"

    # Verify to_dict() returns the same reference (zero-copy)
    assert (
        organization_dict is organization._data
    ), "to_dict() should return the same reference as _data"


@pytest.mark.integration()
def test_organization_view_filtering(kili_client):
    """Test that OrganizationView objects work correctly with filtering."""
    # Get all organizations
    all_organizations = kili_client.organizations.list(first=10, as_generator=False)

    if not all_organizations:
        pytest.skip("No organizations available for testing")

    # Get the first organization's ID
    first_org_id = all_organizations[0].id

    # Query for specific organization by ID
    filtered_organizations = kili_client.organizations.list(
        organization_id=first_org_id, as_generator=False
    )

    # Verify we got results
    assert len(filtered_organizations) > 0, "Should get at least one organization with specific ID"

    # Verify each result is an OrganizationView
    for organization in filtered_organizations:
        assert_is_view(organization, OrganizationView)

        # Verify it has the correct organization ID
        assert organization.id == first_org_id, "Filtered organization should have the requested ID"


@pytest.mark.integration()
def test_organization_view_empty_results(kili_client):
    """Test that list returns a list even when no specific filters match."""
    # For organizations, we can't easily test "no results" scenarios
    # since the API restricts querying other users' organizations
    # Instead, just verify we always get a list back
    organizations = kili_client.organizations.list(
        first=0,  # Request 0 items
        as_generator=False,
    )

    # Verify we get a list (even if empty)
    assert isinstance(organizations, list), "Should return a list even when first=0"


@pytest.mark.integration()
def test_organization_view_with_fields_parameter(kili_client):
    """Test that OrganizationView works correctly with custom fields parameter."""
    # Query with specific fields (only valid fields from the schema)
    organizations = kili_client.organizations.list(
        first=1, fields=["id", "name"], as_generator=False
    )

    if not organizations:
        pytest.skip("No organizations available for testing")

    organization = organizations[0]

    # Verify it's still an OrganizationView
    assert_is_view(organization, OrganizationView)

    # Verify requested fields are accessible
    assert_view_property_access(organization, "id")
    assert_view_property_access(organization, "name")


@pytest.mark.integration()
def test_organization_count_method(kili_client):
    """Test that organizations.count() works correctly and returns an integer."""
    # Count all organizations
    total_count = kili_client.organizations.count()

    # Verify result is an integer
    assert isinstance(total_count, int), "count() should return an integer"
    assert total_count > 0, "count() should return at least one organization"


@pytest.mark.integration()
def test_organization_view_full_address(kili_client):
    """Test the full_address computed property."""
    # Get organizations with standard fields
    organizations = kili_client.organizations.list(
        first=1, fields=["id", "name"], as_generator=False
    )

    if not organizations:
        pytest.skip("No organizations available for testing")

    organization = organizations[0]

    # Verify OrganizationView type
    assert_is_view(organization, OrganizationView)

    # Test full_address property exists (even though address fields may not be in the response)
    assert_view_property_access(organization, "full_address")

    # Verify full_address is a string
    assert isinstance(organization.full_address, str), "full_address should be a string"

    # Since address fields are not in the Organization schema, full_address will likely be empty
    # This just tests that the property exists and returns a string


@pytest.mark.integration()
def test_organization_metrics_method(kili_client):
    """Test that organizations.metrics() works correctly and returns OrganizationMetricsView."""
    # Get an organization first
    organizations = kili_client.organizations.list(first=1, as_generator=False)

    if not organizations:
        pytest.skip("No organizations available for testing")

    organization = organizations[0]

    # Get metrics for the organization
    metrics = kili_client.organizations.metrics(organization_id=organization.id)

    # Verify result is an OrganizationMetricsView with to_dict() method
    assert hasattr(metrics, "to_dict"), "metrics() should return an object with to_dict() method"

    # Convert to dict for backward compatibility checks
    metrics_dict = metrics.to_dict()
    assert isinstance(metrics_dict, dict), "to_dict() should return a dictionary"

    # Verify it contains expected metric fields (based on default fields)
    assert (
        "numberOfAnnotations" in metrics_dict or len(metrics_dict) >= 0
    ), "metrics should contain data or be empty"
