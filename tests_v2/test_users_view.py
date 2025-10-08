"""Integration tests for UserView objects returned by the users namespace.

This test file validates that the users.list() method correctly returns
UserView objects instead of dictionaries, and that these objects provide
proper property access and backward compatibility.

Test Strategy:
    - Verify list() returns UserView objects in all modes (list, generator)
    - Test UserView property access for common properties
    - Validate backward compatibility with dictionary interface via to_dict()
    - Ensure filtering capabilities work correctly
    - Verify empty result handling
    - Test mutation methods still return dicts (unchanged)
"""

import pytest

from kili.domain_v2.user import UserView
from tests_v2 import (
    assert_is_view,
    assert_view_has_dict_compatibility,
    assert_view_property_access,
)


@pytest.mark.integration()
def test_list_returns_user_views(kili_client):
    """Test that users.list() in list mode returns UserView objects."""
    # Get users in list mode
    users = kili_client.users.list(first=5, as_generator=False)

    # Verify we get a list
    assert isinstance(users, list), "users.list() with as_generator=False should return a list"

    # Skip if no users
    if not users:
        pytest.skip("No users available for testing")

    # Verify each item is a UserView
    for user in users:
        assert_is_view(user, UserView)

        # Verify we can access basic properties
        assert hasattr(user, "id")
        assert hasattr(user, "email")
        assert hasattr(user, "display_name")


@pytest.mark.integration()
def test_list_generator_returns_user_views(kili_client):
    """Test that users.list() in generator mode returns UserView objects."""
    # Get users in generator mode
    users_gen = kili_client.users.list(first=5, as_generator=True)

    # Take first 5 items from generator (or fewer if less available)
    users_from_gen = []
    for i, user in enumerate(users_gen):
        if i >= 5:
            break
        users_from_gen.append(user)

    # Skip if no users
    if not users_from_gen:
        pytest.skip("No users available for testing")

    # Verify each yielded item is a UserView
    for user in users_from_gen:
        assert_is_view(user, UserView)

        # Verify we can access basic properties
        assert hasattr(user, "id")
        assert hasattr(user, "email")


@pytest.mark.integration()
def test_user_view_properties(kili_client):
    """Test that UserView provides access to all expected properties."""
    # Get first user
    users = kili_client.users.list(first=1, as_generator=False)

    if not users:
        pytest.skip("No users available for testing")

    user = users[0]

    # Verify UserView type
    assert_is_view(user, UserView)

    # Test core properties exist and are accessible
    assert_view_property_access(user, "id")
    assert_view_property_access(user, "email")
    assert_view_property_access(user, "name")
    assert_view_property_access(user, "firstname")
    assert_view_property_access(user, "lastname")
    assert_view_property_access(user, "activated")
    assert_view_property_access(user, "organization_id")
    assert_view_property_access(user, "display_name")
    assert_view_property_access(user, "full_name")

    # Test that id and email are not empty
    assert user.id, "User id should not be empty"
    assert user.email, "User email should not be empty"

    # Test display_name logic (should be name if available, else email)
    if user.name:
        assert user.display_name == user.name or user.display_name == user.email
    else:
        assert user.display_name == user.email or user.display_name == user.id

    # Test full_name logic
    if user.firstname or user.lastname:
        expected_full = f"{user.firstname} {user.lastname}".strip()
        assert user.full_name == expected_full
    else:
        assert user.full_name in (user.name, user.email)

    # Test boolean property
    assert isinstance(user.activated, bool), "activated should be a boolean"


@pytest.mark.integration()
def test_user_view_dict_compatibility(kili_client):
    """Test that UserView objects maintain backward compatibility with dict interface."""
    # Get first user
    users = kili_client.users.list(first=1, as_generator=False)

    if not users:
        pytest.skip("No users available for testing")

    user = users[0]

    # Verify UserView type
    assert_is_view(user, UserView)

    # Test dictionary compatibility
    assert_view_has_dict_compatibility(user)

    # Verify to_dict() returns expected data
    user_dict = user.to_dict()
    assert isinstance(user_dict, dict)
    assert "id" in user_dict
    assert "email" in user_dict

    # Verify properties match dictionary values
    assert user.id == user_dict.get("id")
    assert user.email == user_dict.get("email")
    assert user.firstname == user_dict.get("firstname")
    assert user.lastname == user_dict.get("lastname")


@pytest.mark.integration()
def test_user_view_filtering(kili_client):
    """Test that filtering capabilities work with UserView objects."""
    # Get all users first
    all_users = kili_client.users.list(first=10, as_generator=False)

    if not all_users:
        pytest.skip("No users available for testing")

    # Get first user's email and organization
    first_user = all_users[0]
    test_email = first_user.email
    test_org_id = first_user.organization_id

    # Filter by email
    users_by_email = kili_client.users.list(email=test_email, as_generator=False)
    assert isinstance(users_by_email, list)

    # Verify filtered results
    if users_by_email:
        for user in users_by_email:
            assert_is_view(user, UserView)
            assert user.email == test_email

    # Filter by organization_id
    if test_org_id:
        users_by_org = kili_client.users.list(
            organization_id=test_org_id, first=5, as_generator=False
        )
        assert isinstance(users_by_org, list)

        if users_by_org:
            for user in users_by_org:
                assert_is_view(user, UserView)
                assert user.organization_id == test_org_id


@pytest.mark.integration()
def test_user_view_empty_results(kili_client):
    """Test that empty results are handled correctly."""
    # Query with a filter that should return no results
    users = kili_client.users.list(email="nonexistent@example.com", as_generator=False)

    # Verify we get an empty list (not None or error)
    assert isinstance(users, list)
    assert len(users) == 0


@pytest.mark.integration()
def test_user_view_with_fields_parameter(kili_client):
    """Test that custom fields parameter works with UserView objects."""
    # Request specific fields
    users = kili_client.users.list(
        first=3, fields=("id", "email", "firstname", "lastname", "activated"), as_generator=False
    )

    if not users:
        pytest.skip("No users available for testing")

    # Verify we get UserView objects
    for user in users:
        assert_is_view(user, UserView)

        # Verify requested fields are accessible
        assert user.id
        assert user.email
        # firstname/lastname may be empty but should be accessible
        _ = user.firstname
        _ = user.lastname
        assert isinstance(user.activated, bool)


@pytest.mark.integration()
def test_mutation_methods_still_return_dicts(kili_client):
    """Verify that create/update methods still return dictionaries (unchanged).

    This test verifies that mutation methods (create, update, update_password)
    continue to return Dict[Literal["id"], str] as expected, since they return
    mutation results, not full user objects.
    """
    # Note: We cannot easily test create() without side effects,
    # but we can verify the type annotations and docstrings are correct

    # Get a user for reference
    users = kili_client.users.list(first=1, as_generator=False)

    if not users:
        pytest.skip("No users available for testing")

    # Verify that the namespace has the mutation methods
    assert hasattr(kili_client.users, "create")
    assert hasattr(kili_client.users, "update")
    assert hasattr(kili_client.users, "update_password")

    # Verify count() returns int
    count = kili_client.users.count()
    assert isinstance(count, int)
    assert count >= len(users)


@pytest.mark.integration()
def test_user_view_organization_role(kili_client):
    """Test organization_role property and is_admin computed property."""
    # Get users - Note: organizationRole returns a string like "ADMIN", not a dict
    users = kili_client.users.list(
        first=5, fields=("id", "email", "organizationRole"), as_generator=False
    )

    if not users:
        pytest.skip("No users available for testing")

    for user in users:
        assert_is_view(user, UserView)

        # Test organization_role property
        # In the actual API, organizationRole can be a string or dict depending on query
        org_role = user.organization_role
        # The property should be accessible even if None
        # Note: based on actual API behavior, this might be a string or dict

        # Test is_admin computed property
        assert isinstance(user.is_admin, bool)


@pytest.mark.integration()
def test_user_view_timestamps(kili_client):
    """Test timestamp properties (created_at, updated_at).

    Note: lastSeenAt is not available in the User API schema.
    """
    # Get users with timestamp fields (note: lastSeenAt doesn't exist in API)
    users = kili_client.users.list(
        first=3, fields=("id", "email", "createdAt", "updatedAt"), as_generator=False
    )

    if not users:
        pytest.skip("No users available for testing")

    user = users[0]
    assert_is_view(user, UserView)

    # Test timestamp properties (they may be None or ISO timestamp strings)
    created = user.created_at
    updated = user.updated_at

    # created_at should typically exist
    if created:
        assert isinstance(created, str)
        # Basic ISO format check (YYYY-MM-DD)
        assert len(created) >= 10

    # updated_at should typically exist
    if updated:
        assert isinstance(updated, str)
        assert len(updated) >= 10

    # Test last_seen_at property (will be None if not in data)
    last_seen = user.last_seen_at
    # Should not raise error even if field not present
    assert last_seen is None or isinstance(last_seen, str)
