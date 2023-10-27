"""Notification use cases."""

from typing import Dict, Generator

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.domain.notification import NotificationFilter
from kili.domain.types import ListOrTuple
from kili.use_cases.base import BaseUseCases


class NotificationUseCases(BaseUseCases):
    """Notification use cases."""

    def list_notifications(
        self, filters: NotificationFilter, fields: ListOrTuple[str], options: QueryOptions
    ) -> Generator[Dict, None, None]:
        """List notifications."""
        return self._kili_api_gateway.list_notifications(
            filters=filters, fields=fields, options=options
        )

    def count_notifications(self, filters: NotificationFilter) -> int:
        """Count notifications."""
        return self._kili_api_gateway.count_notification(filters=filters)
