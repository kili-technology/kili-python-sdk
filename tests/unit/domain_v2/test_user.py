"""Unit tests for User domain contracts."""

from typing import cast

from kili.domain_v2.user import (
    UserContract,
    UserView,
    filter_users_by_activated,
    sort_users_by_email,
    validate_user,
)


class TestUserContract:
    """Test suite for UserContract."""

    def test_validate_user_with_valid_data(self):
        """Test validating a valid user contract."""
        user_data = {
            "id": "user-123",
            "email": "user@example.com",
            "name": "John Doe",
            "firstname": "John",
            "lastname": "Doe",
            "activated": True,
            "createdAt": "2024-01-01T00:00:00Z",
            "organizationId": "org-123",
        }

        result = validate_user(user_data)
        assert result == user_data

    def test_validate_user_with_partial_data(self):
        """Test validating a user with only some fields."""
        user_data = {
            "id": "user-123",
            "email": "user@example.com",
        }

        result = validate_user(user_data)
        assert result == user_data

    def test_validate_user_with_organization_role(self):
        """Test validating a user with organization role."""
        user_data = {
            "id": "user-123",
            "email": "admin@example.com",
            "organizationRole": {
                "id": "role-123",
                "role": "ADMIN",
            },
        }

        result = validate_user(user_data)
        assert result == user_data
        org_role = result.get("organizationRole")
        assert org_role is not None
        assert isinstance(org_role, dict)
        assert org_role.get("role") == "ADMIN"


class TestUserView:
    """Test suite for UserView wrapper."""

    def test_user_view_basic_properties(self):
        """Test basic property access on UserView."""
        user_data = cast(
            UserContract,
            {
                "id": "user-123",
                "email": "user@example.com",
                "name": "John Doe",
                "firstname": "John",
                "lastname": "Doe",
                "activated": True,
            },
        )

        view = UserView(user_data)

        assert view.id == "user-123"
        assert view.email == "user@example.com"
        assert view.name == "John Doe"
        assert view.firstname == "John"
        assert view.lastname == "Doe"
        assert view.activated is True

    def test_user_view_display_name(self):
        """Test display name property."""
        # With name
        user_data = cast(
            UserContract,
            {
                "id": "user-123",
                "email": "user@example.com",
                "name": "John Doe",
            },
        )
        view = UserView(user_data)
        assert view.display_name == "John Doe"

        # Without name
        user_data = cast(
            UserContract,
            {
                "id": "user-123",
                "email": "user@example.com",
            },
        )
        view = UserView(user_data)
        assert view.display_name == "user@example.com"

        # Without name and email
        user_data = cast(UserContract, {"id": "user-123"})
        view = UserView(user_data)
        assert view.display_name == "user-123"

    def test_user_view_full_name(self):
        """Test full name property."""
        # With firstname and lastname
        user_data = cast(
            UserContract,
            {
                "id": "user-123",
                "email": "user@example.com",
                "firstname": "John",
                "lastname": "Doe",
            },
        )
        view = UserView(user_data)
        assert view.full_name == "John Doe"

        # Only firstname
        user_data = cast(
            UserContract,
            {
                "id": "user-123",
                "email": "user@example.com",
                "firstname": "John",
            },
        )
        view = UserView(user_data)
        assert view.full_name == "John"

        # Only lastname
        user_data = cast(
            UserContract,
            {
                "id": "user-123",
                "email": "user@example.com",
                "lastname": "Doe",
            },
        )
        view = UserView(user_data)
        assert view.full_name == "Doe"

        # No firstname/lastname, fallback to name
        user_data = cast(
            UserContract,
            {
                "id": "user-123",
                "email": "user@example.com",
                "name": "John Doe",
            },
        )
        view = UserView(user_data)
        assert view.full_name == "John Doe"

        # No name info, fallback to email
        user_data = cast(
            UserContract,
            {
                "id": "user-123",
                "email": "user@example.com",
            },
        )
        view = UserView(user_data)
        assert view.full_name == "user@example.com"

    def test_user_view_organization_role(self):
        """Test organization role property."""
        user_data = cast(
            UserContract,
            {
                "id": "user-123",
                "email": "user@example.com",
                "organizationRole": {
                    "id": "role-123",
                    "role": "ADMIN",
                },
            },
        )

        view = UserView(user_data)

        assert view.organization_role is not None
        assert isinstance(view.organization_role, dict)
        assert view.organization_role.get("role") == "ADMIN"

    def test_user_view_is_admin(self):
        """Test is_admin property."""
        # Admin user
        user_data = cast(
            UserContract,
            {
                "id": "user-123",
                "email": "admin@example.com",
                "organizationRole": {"id": "role-123", "role": "ADMIN"},
            },
        )
        view = UserView(user_data)
        assert view.is_admin is True

        # Non-admin user
        user_data = cast(
            UserContract,
            {
                "id": "user-123",
                "email": "user@example.com",
                "organizationRole": {"id": "role-123", "role": "USER"},
            },
        )
        view = UserView(user_data)
        assert view.is_admin is False

        # User without role
        user_data = cast(UserContract, {"id": "user-123", "email": "user@example.com"})
        view = UserView(user_data)
        assert view.is_admin is False

    def test_user_view_organization_id(self):
        """Test organization ID property."""
        user_data = cast(
            UserContract,
            {
                "id": "user-123",
                "email": "user@example.com",
                "organizationId": "org-123",
            },
        )

        view = UserView(user_data)
        assert view.organization_id == "org-123"

    def test_user_view_phone(self):
        """Test phone property."""
        user_data = cast(
            UserContract,
            {
                "id": "user-123",
                "email": "user@example.com",
                "phone": "+1234567890",
            },
        )

        view = UserView(user_data)
        assert view.phone == "+1234567890"

        # Without phone
        user_data = cast(UserContract, {"id": "user-123", "email": "user@example.com"})
        view = UserView(user_data)
        assert view.phone is None

    def test_user_view_timestamps(self):
        """Test timestamp properties."""
        user_data = cast(
            UserContract,
            {
                "id": "user-123",
                "email": "user@example.com",
                "createdAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-15T10:30:00Z",
                "lastSeenAt": "2024-01-20T14:45:00Z",
            },
        )

        view = UserView(user_data)

        assert view.created_at == "2024-01-01T00:00:00Z"
        assert view.updated_at == "2024-01-15T10:30:00Z"
        assert view.last_seen_at == "2024-01-20T14:45:00Z"

    def test_user_view_to_dict(self):
        """Test converting view back to dictionary."""
        user_data = cast(
            UserContract,
            {
                "id": "user-123",
                "email": "user@example.com",
                "name": "John Doe",
            },
        )

        view = UserView(user_data)
        result = view.to_dict()

        assert result == user_data
        assert result is user_data

    def test_user_view_missing_fields(self):
        """Test accessing missing fields returns appropriate defaults."""
        user_data = cast(UserContract, {"id": "user-123"})
        view = UserView(user_data)

        assert view.email == ""
        assert view.name == ""
        assert view.firstname == ""
        assert view.lastname == ""
        assert view.activated is False
        assert view.organization_id == ""
        assert view.organization_role is None
        assert view.phone is None
        assert view.created_at is None
        assert view.updated_at is None
        assert view.last_seen_at is None


class TestUserHelpers:
    """Test suite for user helper functions."""

    def test_sort_users_by_email_ascending(self):
        """Test sorting users by email in ascending order."""
        users = [
            cast(UserContract, {"id": "user-3", "email": "charlie@example.com"}),
            cast(UserContract, {"id": "user-1", "email": "alice@example.com"}),
            cast(UserContract, {"id": "user-2", "email": "bob@example.com"}),
        ]

        sorted_users = sort_users_by_email(users, reverse=False)

        assert sorted_users[0].get("email") == "alice@example.com"
        assert sorted_users[1].get("email") == "bob@example.com"
        assert sorted_users[2].get("email") == "charlie@example.com"

    def test_sort_users_by_email_descending(self):
        """Test sorting users by email in descending order."""
        users = [
            cast(UserContract, {"id": "user-1", "email": "alice@example.com"}),
            cast(UserContract, {"id": "user-3", "email": "charlie@example.com"}),
            cast(UserContract, {"id": "user-2", "email": "bob@example.com"}),
        ]

        sorted_users = sort_users_by_email(users, reverse=True)

        assert sorted_users[0].get("email") == "charlie@example.com"
        assert sorted_users[1].get("email") == "bob@example.com"
        assert sorted_users[2].get("email") == "alice@example.com"

    def test_sort_users_with_missing_email(self):
        """Test sorting users when some lack email."""
        users = [
            cast(UserContract, {"id": "user-2", "email": "bob@example.com"}),
            cast(UserContract, {"id": "user-no-email"}),
            cast(UserContract, {"id": "user-1", "email": "alice@example.com"}),
        ]

        sorted_users = sort_users_by_email(users)

        # User without email should come first (empty string sorts first)
        assert sorted_users[0].get("id") == "user-no-email"

    def test_filter_users_by_activated_true(self):
        """Test filtering for activated users."""
        users = [
            cast(UserContract, {"id": "user-1", "email": "user1@example.com", "activated": True}),
            cast(UserContract, {"id": "user-2", "email": "user2@example.com", "activated": False}),
            cast(UserContract, {"id": "user-3", "email": "user3@example.com", "activated": True}),
            cast(UserContract, {"id": "user-4", "email": "user4@example.com", "activated": False}),
        ]

        filtered = filter_users_by_activated(users, activated=True)

        assert len(filtered) == 2
        assert filtered[0].get("id") == "user-1"
        assert filtered[1].get("id") == "user-3"

    def test_filter_users_by_activated_false(self):
        """Test filtering for deactivated users."""
        users = [
            cast(UserContract, {"id": "user-1", "email": "user1@example.com", "activated": True}),
            cast(UserContract, {"id": "user-2", "email": "user2@example.com", "activated": False}),
            cast(UserContract, {"id": "user-3", "email": "user3@example.com", "activated": True}),
            cast(UserContract, {"id": "user-4", "email": "user4@example.com", "activated": False}),
        ]

        filtered = filter_users_by_activated(users, activated=False)

        assert len(filtered) == 2
        assert filtered[0].get("id") == "user-2"
        assert filtered[1].get("id") == "user-4"

    def test_filter_users_by_activated_no_matches(self):
        """Test filtering when no users match."""
        users = [
            cast(UserContract, {"id": "user-1", "email": "user1@example.com", "activated": True}),
            cast(UserContract, {"id": "user-2", "email": "user2@example.com", "activated": True}),
        ]

        filtered = filter_users_by_activated(users, activated=False)

        assert len(filtered) == 0

    def test_filter_users_with_missing_activated(self):
        """Test filtering users when some lack activated field."""
        users = [
            cast(UserContract, {"id": "user-1", "email": "user1@example.com", "activated": True}),
            cast(UserContract, {"id": "user-2", "email": "user2@example.com"}),  # Missing activated
            cast(UserContract, {"id": "user-3", "email": "user3@example.com", "activated": False}),
        ]

        # Filter for activated=True (user without field won't match)
        filtered = filter_users_by_activated(users, activated=True)
        assert len(filtered) == 1
        assert filtered[0].get("id") == "user-1"
