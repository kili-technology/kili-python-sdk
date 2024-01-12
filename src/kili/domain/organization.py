"""Organization domain."""

from dataclasses import dataclass
from datetime import datetime
from typing import NewType, Optional

OrganizationId = NewType("OrganizationId", str)


@dataclass(frozen=True)
class OrganizationFilters:
    """Dataclass to the OrganizationQuery to filter the results."""

    email: Optional[str] = None
    organization_id: Optional[OrganizationId] = None


@dataclass(frozen=True)
class OrganizationMetricsFilters:
    """Dataclass to the OrganizationQuery to filter the results."""

    id: OrganizationId
    start_datetime: datetime
    end_datetime: datetime


@dataclass(frozen=True)
class OrganizationToCreateInput:
    """Organization to create use case input."""

    name: str
    address: str
    city: str
    country: str
    zip_code: str


@dataclass(frozen=True)
class OrganizationToUpdateInput:
    """Organization to update use case input."""

    name: Optional[str] = None
    license: Optional[dict] = None
