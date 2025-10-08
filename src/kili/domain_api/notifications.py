"""Notifications domain namespace for the Kili Python SDK."""

from typing import Generator, List, Literal, Optional, Union, overload

from typeguard import typechecked

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.domain.notification import NotificationFilter, NotificationId
from kili.domain.types import ListOrTuple
from kili.domain.user import UserFilter, UserId
from kili.domain_api.base import DomainNamespace
from kili.domain_v2.notification import NotificationView, validate_notification
from kili.entrypoints.mutations.notification.queries import (
    GQL_CREATE_NOTIFICATION,
    GQL_UPDATE_PROPERTIES_IN_NOTIFICATION,
)
from kili.use_cases.notification import NotificationUseCases


class NotificationsNamespace(DomainNamespace):
    """Notifications domain namespace providing notification-related operations.

    This namespace provides access to all notification-related functionality
    including creating, updating, querying, and managing notifications.

    The namespace provides the following main operations:
    - list(): Query and list notifications with filtering options
    - count(): Count notifications matching criteria
    - create(): Create new notifications (admin-only)
    - update(): Update existing notifications (admin-only)

    Examples:
        >>> kili = Kili()
        >>> # List all notifications for current user
        >>> notifications = kili.notifications.list()

        >>> # List unseen notifications
        >>> unseen = kili.notifications.list(has_been_seen=False)

        >>> # Count notifications
        >>> count = kili.notifications.count()

        >>> # Get a specific notification
        >>> notification = kili.notifications.list(notification_id="notif_123")

        >>> # Create a new notification (admin only)
        >>> result = kili.notifications.create(
        ...     message="Task completed",
        ...     status="info",
        ...     url="/project/123",
        ...     user_id="user_456"
        ... )

        >>> # Update notification status (admin only)
        >>> kili.notifications.update(
        ...     notification_id="notif_123",
        ...     has_been_seen=True,
        ...     status="read"
        ... )
    """

    def __init__(self, client, gateway):
        """Initialize the notifications namespace.

        Args:
            client: The Kili client instance
            gateway: The KiliAPIGateway instance for API operations
        """
        super().__init__(client, gateway, "notifications")

    @overload
    def list(
        self,
        fields: Optional[ListOrTuple[str]] = None,
        first: Optional[int] = None,
        has_been_seen: Optional[bool] = None,
        notification_id: Optional[str] = None,
        skip: int = 0,
        user_id: Optional[str] = None,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: Literal[True],
    ) -> Generator[NotificationView, None, None]:
        ...

    @overload
    def list(
        self,
        fields: Optional[ListOrTuple[str]] = None,
        first: Optional[int] = None,
        has_been_seen: Optional[bool] = None,
        notification_id: Optional[str] = None,
        skip: int = 0,
        user_id: Optional[str] = None,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: Literal[False] = False,
    ) -> List[NotificationView]:
        ...

    @typechecked
    def list(
        self,
        fields: Optional[ListOrTuple[str]] = None,
        first: Optional[int] = None,
        has_been_seen: Optional[bool] = None,
        notification_id: Optional[str] = None,
        skip: int = 0,
        user_id: Optional[str] = None,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: bool = False,
    ) -> Union[List[NotificationView], Generator[NotificationView, None, None]]:
        """List notifications matching the specified criteria.

        Args:
            fields: List of fields to return for each notification.
                If None, returns default fields: createdAt, hasBeenSeen, id, message, status, userID.
                See the API documentation for all available fields.
            has_been_seen: Filter notifications by their seen status.
                - True: Only seen notifications
                - False: Only unseen notifications
                - None: All notifications (default)
            notification_id: Return only the notification with this specific ID.
            user_id: Filter notifications for a specific user ID.
            first: Maximum number of notifications to return.
            skip: Number of notifications to skip (for pagination).
            disable_tqdm: Whether to disable the progress bar.
            as_generator: If True, returns a generator instead of a list.

        Returns:
            List of notification dictionaries or a generator yielding notification dictionaries.

        Examples:
            >>> # Get all notifications
            >>> notifications = kili.notifications.list()

            >>> # Get unseen notifications only
            >>> unseen = kili.notifications.list(has_been_seen=False)

            >>> # Get specific fields only
            >>> notifications = kili.notifications.list(
            ...     fields=["id", "message", "status", "createdAt"]
            ... )

            >>> # Get notifications for a specific user
            >>> user_notifications = kili.notifications.list(user_id="user_123")

            >>> # Use as generator for memory efficiency
            >>> for notification in kili.notifications.list(as_generator=True):
            ...     print(notification["message"])
        """
        if fields is None:
            fields = ("createdAt", "hasBeenSeen", "id", "message", "status", "userID")

        if disable_tqdm is None:
            disable_tqdm = as_generator

        options = QueryOptions(disable_tqdm, first, skip)
        filters = NotificationFilter(
            has_been_seen=has_been_seen,
            id=NotificationId(notification_id) if notification_id else None,
            user=UserFilter(id=UserId(user_id)) if user_id else None,
        )

        notifications_gen = NotificationUseCases(self.gateway).list_notifications(
            options=options, fields=fields, filters=filters
        )

        if as_generator:
            return (NotificationView(validate_notification(item)) for item in notifications_gen)
        return [NotificationView(validate_notification(item)) for item in notifications_gen]

    @typechecked
    def count(
        self,
        has_been_seen: Optional[bool] = None,
        user_id: Optional[str] = None,
        notification_id: Optional[str] = None,
    ) -> int:
        """Count the number of notifications matching the specified criteria.

        Args:
            has_been_seen: Filter on notifications that have been seen.
                - True: Count only seen notifications
                - False: Count only unseen notifications
                - None: Count all notifications (default)
            user_id: Filter on notifications for a specific user ID.
            notification_id: Filter on a specific notification ID.

        Returns:
            The number of notifications matching the criteria.

        Examples:
            >>> # Count all notifications
            >>> total = kili.notifications.count()

            >>> # Count unseen notifications
            >>> unseen_count = kili.notifications.count(has_been_seen=False)

            >>> # Count notifications for a specific user
            >>> user_count = kili.notifications.count(user_id="user_123")
        """
        filters = NotificationFilter(
            has_been_seen=has_been_seen,
            id=NotificationId(notification_id) if notification_id else None,
            user=UserFilter(id=UserId(user_id)) if user_id else None,
        )
        return NotificationUseCases(self.gateway).count_notifications(filters=filters)

    @typechecked
    def create(
        self,
        message: str,
        status: str,
        url: str,
        user_id: str,
    ) -> NotificationView:
        """Create a new notification.

        This method is currently only available for Kili administrators.

        Args:
            message: The notification message content.
            status: The notification status (e.g., "info", "success", "warning", "error").
            url: The URL associated with the notification.
            user_id: The ID of the user who should receive the notification.

        Returns:
            A NotificationView with the created notification information.

        Examples:
            >>> # Create an info notification
            >>> notification = kili.notifications.create(
            ...     message="Your project export is ready",
            ...     status="info",
            ...     url="/project/123/export",
            ...     user_id="user_456"
            ... )
            >>> print(notification.id)
            'notif_789'
            >>> print(notification.message)
            'Your project export is ready'
            >>> print(notification.status)
            'info'
        """
        # Access the mutations directly from the gateway's GraphQL client
        # This follows the pattern used in other domain namespaces
        variables = {
            "data": {
                "message": message,
                "progress": None,
                "status": status,
                "url": url,
                "userID": user_id,
            }
        }

        result = self.gateway.graphql_client.execute(GQL_CREATE_NOTIFICATION, variables)
        notification_data = result["data"]["data"]
        return NotificationView(validate_notification(notification_data))

    @typechecked
    def update(
        self,
        notification_id: str,
        has_been_seen: Optional[bool] = None,
        status: Optional[str] = None,
        url: Optional[str] = None,
        progress: Optional[int] = None,
        task_id: Optional[str] = None,
    ) -> NotificationView:
        """Update an existing notification.

        This method is currently only available for Kili administrators.

        Args:
            notification_id: The ID of the notification to update.
            has_been_seen: Whether the notification has been seen by the user.
            status: The new status for the notification.
            url: The new URL associated with the notification.
            progress: Progress value for the notification (0-100).
            task_id: Associated task ID for the notification.

        Returns:
            A NotificationView with the updated notification information.

        Examples:
            >>> # Mark notification as seen
            >>> notification = kili.notifications.update(
            ...     notification_id="notif_123",
            ...     has_been_seen=True
            ... )
            >>> print(notification.has_been_seen)
            True

            >>> # Update notification status and URL
            >>> notification = kili.notifications.update(
            ...     notification_id="notif_123",
            ...     status="completed",
            ...     url="/project/123/results"
            ... )
            >>> print(notification.status)
            'completed'
            >>> print(notification.url)
            '/project/123/results'

            >>> # Update progress for a long-running task
            >>> notification = kili.notifications.update(
            ...     notification_id="notif_123",
            ...     progress=75
            ... )
        """
        variables = {
            "id": notification_id,
            "hasBeenSeen": has_been_seen,
            "progress": progress,
            "status": status,
            "taskId": task_id,
            "url": url,
        }

        result = self.gateway.graphql_client.execute(
            GQL_UPDATE_PROPERTIES_IN_NOTIFICATION, variables
        )
        notification_data = result["data"]["data"]
        return NotificationView(validate_notification(notification_data))
