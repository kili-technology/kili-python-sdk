"""Event domain."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, NamedTuple, Optional

from typing_extensions import TypedDict

from kili.core.constants import QUERY_BATCH_SIZE

if TYPE_CHECKING:
    from .project import ProjectId
    from .user import UserId

OrderType = Literal["asc", "desc"]


@dataclass
class EventFilters:
    """Event filters for running an event search."""

    project_id: "ProjectId"
    created_at_gte: Optional[str] = None
    created_at_lte: Optional[str] = None
    user_id: Optional["UserId"] = None
    event: Optional[str] = None
    organization_id: Optional[str] = None


class EventDict(TypedDict):
    """Dict that represents an Event."""

    created_at: str
    event: str
    id: str
    organization_id: str
    payload: dict
    project_id: str
    user_id: str


class QueryOptions(NamedTuple):
    """Options when calling GraphQLQuery from the SDK."""

    first: Optional[int] = None
    skip: int = 0
    batch_size: int = QUERY_BATCH_SIZE
    from_event_id: Optional[str] = None
    until_event_id: Optional[str] = None
    order: Optional[OrderType] = "asc"
