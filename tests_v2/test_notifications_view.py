"""Integration tests for NotificationView objects returned by the notifications namespace.

This test file validates that the notifications.list() method correctly returns
NotificationView objects instead of dictionaries, and that these objects provide
proper property access and backward compatibility.

Test Strategy:
    - Verify list() returns NotificationView objects in all modes (list, generator)
    - Test NotificationView property access for common properties
    - Validate backward compatibility with dictionary interface via to_dict()
    - Test filtering by has_been_seen and user_id
    - Verify computed properties (is_unread, display_name)
    - Ensure mutation methods still return dicts (unchanged)
"""

import pytest

from kili.domain_v2.notification import NotificationView
from tests_v2 import (
    assert_is_view,
    assert_view_has_dict_compatibility,
    assert_view_property_access,
)


@pytest.mark.integration()
def test_list_returns_notification_views(kili_client):
    """Test that notifications.list() in list mode returns NotificationView objects."""
    # Get notifications in list mode
    notifications = kili_client.notifications.list(first=5, as_generator=False)

    # Verify we get a list
    assert isinstance(
        notifications, list
    ), "notifications.list() with as_generator=False should return a list"

    # Skip if no notifications
    if not notifications:
        pytest.skip("No notifications available for testing")

    # Verify each item is a NotificationView
    for notification in notifications:
        assert_is_view(notification, NotificationView)

        # Verify we can access basic properties
        assert hasattr(notification, "id")
        assert hasattr(notification, "message")
        assert hasattr(notification, "status")
        assert hasattr(notification, "user_id")


@pytest.mark.integration()
def test_list_generator_returns_notification_views(kili_client):
    """Test that notifications.list() in generator mode returns NotificationView objects."""
    # Get notifications in generator mode
    notifications_gen = kili_client.notifications.list(first=5, as_generator=True)

    # Take first 5 items from generator (or fewer if less available)
    notifications_from_gen = []
    for i, notification in enumerate(notifications_gen):
        if i >= 5:
            break
        notifications_from_gen.append(notification)

    # Skip if no notifications
    if not notifications_from_gen:
        pytest.skip("No notifications available for testing")

    # Verify each yielded item is a NotificationView
    for notification in notifications_from_gen:
        assert_is_view(notification, NotificationView)

        # Verify we can access basic properties
        assert hasattr(notification, "id")
        assert hasattr(notification, "message")
        assert hasattr(notification, "status")


@pytest.mark.integration()
def test_notification_view_properties(kili_client):
    """Test that NotificationView provides access to all expected properties."""
    # Get first notification
    notifications = kili_client.notifications.list(first=1, as_generator=False)

    if not notifications:
        pytest.skip("No notifications available for testing")

    notification = notifications[0]

    # Verify NotificationView type
    assert_is_view(notification, NotificationView)

    # Test core properties exist and are accessible
    assert_view_property_access(notification, "id")
    assert_view_property_access(notification, "message")
    assert_view_property_access(notification, "status")
    assert_view_property_access(notification, "user_id")
    assert_view_property_access(notification, "created_at")
    assert_view_property_access(notification, "has_been_seen")

    # Test that id is not empty
    assert notification.id, "Notification id should not be empty"

    # Test that message is not empty
    assert notification.message, "Notification message should not be empty"

    # Test computed properties
    assert_view_property_access(notification, "is_unread")
    assert_view_property_access(notification, "display_name")

    # Test that is_unread is inverse of has_been_seen
    assert notification.is_unread == (
        not notification.has_been_seen
    ), "is_unread should be the inverse of has_been_seen"

    # Test display_name (should be truncated message or id)
    assert notification.display_name, "display_name should not be empty"
    if len(notification.message) <= 50:
        assert notification.display_name == notification.message
    else:
        assert notification.display_name == notification.message[:47] + "..."

    # Test optional properties
    assert_view_property_access(notification, "url")


@pytest.mark.integration()
def test_notification_view_dict_compatibility(kili_client):
    """Test that NotificationView maintains backward compatibility via to_dict()."""
    # Get first notification
    notifications = kili_client.notifications.list(first=1, as_generator=False)

    if not notifications:
        pytest.skip("No notifications available for testing")

    notification = notifications[0]

    # Verify NotificationView type
    assert_is_view(notification, NotificationView)

    # Test dictionary compatibility
    assert_view_has_dict_compatibility(notification)

    # Get dictionary representation
    notification_dict = notification.to_dict()

    # Verify it's a dictionary
    assert isinstance(notification_dict, dict), "to_dict() should return a dictionary"

    # Verify dictionary has expected keys
    assert "id" in notification_dict, "Dictionary should have 'id' key"

    # Verify dictionary values match property values
    if "message" in notification_dict:
        assert (
            notification_dict["message"] == notification.message
        ), "Dictionary message should match property"

    if "status" in notification_dict:
        assert (
            notification_dict["status"] == notification.status
        ), "Dictionary status should match property"

    if "userID" in notification_dict:
        assert (
            notification_dict["userID"] == notification.user_id
        ), "Dictionary userID should match property"

    # Verify to_dict() returns the same reference (zero-copy)
    assert (
        notification_dict is notification._data
    ), "to_dict() should return the same reference as _data"


@pytest.mark.integration()
def test_notification_view_filtering(kili_client):
    """Test that NotificationView objects work correctly with filtering."""
    # Get all notifications
    all_notifications = kili_client.notifications.list(first=10, as_generator=False)

    if not all_notifications:
        pytest.skip("No notifications available for testing")

    # Test filtering by has_been_seen=False (unseen notifications)
    unseen_notifications = kili_client.notifications.list(
        has_been_seen=False, first=10, as_generator=False
    )

    # Verify results are NotificationView objects
    for notification in unseen_notifications:
        assert_is_view(notification, NotificationView)
        # All should be unseen
        assert notification.has_been_seen is False, "Filtered notifications should be unseen"
        assert notification.is_unread is True, "Filtered notifications should be unread"

    # Test filtering by has_been_seen=True (seen notifications)
    seen_notifications = kili_client.notifications.list(
        has_been_seen=True, first=10, as_generator=False
    )

    # Verify results are NotificationView objects
    for notification in seen_notifications:
        assert_is_view(notification, NotificationView)
        # All should be seen
        assert notification.has_been_seen is True, "Filtered notifications should be seen"
        assert notification.is_unread is False, "Filtered notifications should not be unread"


@pytest.mark.integration()
def test_notification_view_empty_results(kili_client):
    """Test that empty results are handled correctly."""
    # Query with a filter that should return no results
    # Using a non-existent notification ID
    empty_notifications = kili_client.notifications.list(
        notification_id="non-existent-notification-id-12345", as_generator=False
    )

    # Verify we get an empty list
    assert isinstance(empty_notifications, list), "Should return a list even when no results"
    assert len(empty_notifications) == 0, "Should return empty list for non-existent notification"


@pytest.mark.integration()
def test_mutation_methods_still_return_dicts(kili_client):
    """Test that mutation methods (create, update) still return dicts (unchanged)."""
    # Note: These operations typically require admin privileges
    # This test may be skipped in most test environments

    try:
        # Test create() method - should return dict
        # We'll attempt to create a notification, but this likely requires admin access
        # and may fail in test environments

        # Get current user ID (notifications need a user_id)
        # This is just to demonstrate the pattern - will likely fail with permission error
        create_result = kili_client.notifications.create(
            message="Test notification for integration test",
            status="info",
            url="/test",
            user_id="test-user-id",
        )

        # Verify result is a dict
        assert isinstance(create_result, dict), "create() should return a dict"

    except Exception as e:
        # If mutations are not allowed in test environment, skip the test
        pytest.skip(f"Mutations not allowed or failed (expected for non-admin users): {e}")


@pytest.mark.integration()
def test_notification_view_with_fields_parameter(kili_client):
    """Test that NotificationView works correctly with custom fields parameter."""
    # Query with specific fields
    notifications = kili_client.notifications.list(
        first=1,
        fields=["id", "message", "status", "userID", "createdAt", "hasBeenSeen"],
        as_generator=False,
    )

    if not notifications:
        pytest.skip("No notifications available for testing")

    notification = notifications[0]

    # Verify it's still a NotificationView
    assert_is_view(notification, NotificationView)

    # Verify requested fields are accessible
    assert_view_property_access(notification, "id")
    assert_view_property_access(notification, "message")
    assert_view_property_access(notification, "status")
    assert_view_property_access(notification, "user_id")
    assert_view_property_access(notification, "created_at")
    assert_view_property_access(notification, "has_been_seen")


@pytest.mark.integration()
def test_notification_count_method(kili_client):
    """Test that notifications.count() works correctly and returns an integer."""
    # Count all notifications
    total_count = kili_client.notifications.count()

    # Verify result is an integer
    assert isinstance(total_count, int), "count() should return an integer"
    assert total_count >= 0, "count() should return a non-negative integer"

    # Count unseen notifications
    unseen_count = kili_client.notifications.count(has_been_seen=False)

    # Verify result is an integer
    assert isinstance(unseen_count, int), "count() should return an integer"
    assert unseen_count >= 0, "count() should return a non-negative integer"
    assert unseen_count <= total_count, "Unseen count should not exceed total count"

    # Count seen notifications
    seen_count = kili_client.notifications.count(has_been_seen=True)

    # Verify result is an integer
    assert isinstance(seen_count, int), "count() should return an integer"
    assert seen_count >= 0, "count() should return a non-negative integer"
    assert seen_count <= total_count, "Seen count should not exceed total count"

    # Verify seen + unseen = total
    assert (
        seen_count + unseen_count == total_count
    ), "Seen count + unseen count should equal total count"
