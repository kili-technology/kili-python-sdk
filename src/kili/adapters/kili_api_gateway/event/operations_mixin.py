"""Mixin extending Kili API Gateway class with Api Keys related operations."""

from typing import List, Optional, cast

from kili.adapters.kili_api_gateway.base import BaseOperationMixin
from kili.adapters.kili_api_gateway.event.mappers import (
    event_pagination_wrapper,
    event_where_wrapper,
)
from kili.adapters.kili_api_gateway.event.operations import get_events_query
from kili.adapters.kili_api_gateway.event.queries import (
    PaginatedGraphQLQuery,
)
from kili.adapters.kili_api_gateway.helpers.queries import fragment_builder
from kili.domain.event import EventDict, EventFilters, QueryOptions
from kili.domain.types import ListOrTuple

DEFAULT_EVENT_FIELDS = [
    "createdAt",
    "event",
    "id",
    "organizationId",
    "payload",
    "projectId",
    "userId",
]


class EventOperationMixin(BaseOperationMixin):
    """Mixin extending Kili API Gateway class with event related operations."""

    def list_events(
        self,
        filters: EventFilters,
        options: QueryOptions,
        fields: Optional[ListOrTuple[str]] = None,
    ) -> List[EventDict]:
        """List events with given options."""
        fragment = fragment_builder(fields or DEFAULT_EVENT_FIELDS)
        query = get_events_query(fragment)
        where = event_where_wrapper(filters)
        pagination = event_pagination_wrapper(options)

        return [
            cast(EventDict, item)
            for item in PaginatedGraphQLQuery(
                self.graphql_client
            ).execute_query_from_paginated_call(
                query,
                where,
                pagination,
                options,
            )
        ]
