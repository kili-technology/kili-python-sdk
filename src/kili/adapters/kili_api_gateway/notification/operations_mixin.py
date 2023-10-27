"""Mixin extending Kili API Gateway class with notification-related operations."""

from typing import Dict, Generator

from kili.adapters.kili_api_gateway.base import BaseOperationMixin
from kili.adapters.kili_api_gateway.helpers.queries import (
    PaginatedGraphQLQuery,
    QueryOptions,
    fragment_builder,
)
from kili.domain.notification import NotificationFilter
from kili.domain.types import ListOrTuple

from .mappers import map_notification_filter
from .operations import GQL_COUNT_NOTIFICATIONS, get_notifications_query


class NotificationOperationMixin(BaseOperationMixin):
    """GraphQL Mixin extending GraphQL Gateway class with notification-related operations."""

    def list_notifications(
        self, filters: NotificationFilter, fields: ListOrTuple[str], options: QueryOptions
    ) -> Generator[Dict, None, None]:
        """List notifications."""
        fragment = fragment_builder(fields)
        query = get_notifications_query(fragment)
        where = map_notification_filter(filters=filters)
        return PaginatedGraphQLQuery(self.graphql_client).execute_query_from_paginated_call(
            query, where, options, "Retrieving notifications", GQL_COUNT_NOTIFICATIONS
        )

    def count_notification(self, filters: NotificationFilter) -> int:
        """Count notifications."""
        variables = {"where": map_notification_filter(filters=filters)}
        return self.graphql_client.execute(GQL_COUNT_NOTIFICATIONS, variables)["data"]
