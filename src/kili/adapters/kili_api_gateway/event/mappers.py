"""GraphQL payload data mappers for api keys operations."""

from typing import Dict

from kili.domain.event import EventFilters, QueryOptions


def event_where_wrapper(filter: EventFilters) -> Dict:
    """Build the GraphQL EventMapperWhere variable to be sent in an operation."""
    return {
        "organizationId": filter.organization_id,
        "projectId": filter.project_id,
        "createdAtGte": filter.created_at_gte,
        "createdAtLte": filter.created_at_lte,
        "userId": filter.user_id,
        "event": filter.event,
    }


def event_pagination_wrapper(options: QueryOptions) -> Dict:
    """Build the GraphQL EventMapperPagination variable to be sent in an operation."""
    return {
        "fromEventId": options.from_event_id,
        "untilEventId": options.until_event_id,
    }
