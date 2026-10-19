"""Mappers for notification API calls."""

from kili.domain.notification import NotificationFilter


def map_notification_filter(filters: NotificationFilter) -> dict:
    """Build the GraphQL NotificationWhere variable to be sent in an operation."""
    return {"id": filters.id}
