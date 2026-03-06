"""Mappers for notification API calls."""


from kili.adapters.kili_api_gateway.user.mappers import user_where_mapper
from kili.domain.notification import NotificationFilter


def map_notification_filter(filters: NotificationFilter) -> dict:
    """Build the GraphQL NotificationWhere variable to be sent in an operation."""
    return {
        "hasBeenSeen": filters.has_been_seen,
        "id": filters.id,
        "user": user_where_mapper(filters.user) if filters.user else None,
    }
