"""Organization domain."""
from dataclasses import dataclass
from typing import NewType, Optional

OrganizationId = NewType("OrganizationId", str)

Organization = NewType("Organization", dict)


@dataclass
class OrganizationFilters:
    """Dataclass to the OrganizationQuery to filter the results."""

    email: Optional[str] = None
    organization_id: Optional[OrganizationId] = None
