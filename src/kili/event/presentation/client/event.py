"""Client presentation methods for labels."""

# pylint: disable=too-many-lines
from typing import List, Optional

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.domain.event import EventDict, EventFilters, OrderType, QueryOptions
from kili.domain.project import ProjectId
from kili.domain.user import UserId
from kili.utils.logcontext import for_all_methods, log_call


@for_all_methods(log_call, exclude=["__init__"])
class EventClientMethods:
    def __init__(self, kili_api_gateway: KiliAPIGateway):
        self.kili_api_gateway = kili_api_gateway

    def list(
        self,
        project_id: str,
        fields: Optional[List[str]] = None,
        created_at_gte: Optional[str] = None,
        created_at_lte: Optional[str] = None,
        user_id: Optional[str] = None,
        event: Optional[str] = None,
        skip: int = 0,
        from_event_id: Optional[str] = None,
        until_event_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        order: Optional[OrderType] = "asc",
    ) -> List[EventDict]:
        """List events of my project.

        Args:
            project_id: Identifier of the project.
            fields: All the fields to request among the possible fields for the events.
                Defaults is ["createdAt", "event", "id", "organizationId", "payload", "projectId", "userId"].
            created_at_gte: Filter events created after this date.
            created_at_lte: Filter events created before this date.
            user_id: Filter events by user id.
            event: Filter events by event type.
            skip: Number of events to skip.
            from_event_id: Filter events from this event id.
            until_event_id: Filter events until this event id.
            order: Order of the events. Can be "asc" or "desc".

        Returns:
            A list of events.

        Examples:
            >>> kili.events.list(project_id="your_project_id")
        """
        converted_filters = EventFilters(
            project_id=ProjectId(project_id),
            organization_id=organization_id,
            created_at_gte=created_at_gte,
            created_at_lte=created_at_lte,
            user_id=UserId(user_id) if user_id else None,
            event=event,
        )
        options = QueryOptions(
            skip=skip,
            from_event_id=from_event_id,
            until_event_id=until_event_id,
            order=order,
        )

        return list(
            self.kili_api_gateway.list_events(
                filters=converted_filters, options=options, fields=fields
            )
        )
