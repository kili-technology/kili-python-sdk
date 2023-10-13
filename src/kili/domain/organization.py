"""Organization domain."""
from dataclasses import dataclass
from datetime import datetime
from typing import NewType, Optional

OrganizationId = NewType("OrganizationId", str)

Organization = NewType("Organization", dict)


@dataclass(frozen=True)
class OrganizationFilters:
    """Dataclass to the OrganizationQuery to filter the results."""

    email: Optional[str] = None
    organization_id: Optional[OrganizationId] = None


@dataclass(frozen=True)
class OrganizationMetricsFilters:
    """Dataclass to the OrganizationQuery to filter the results."""

    id: OrganizationId  # noqa: A003
    start_datetime: datetime
    end_datetime: datetime
