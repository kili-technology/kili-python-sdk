"""Organization types for Kili API Gateway."""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class KiliAPIGateWayCreateOrganizationInput:
    """Organization to create Kili API Gateway input."""

    name: str
    address: str
    city: str
    country: str
    zip_code: str


@dataclass(frozen=True)
class KiliAPIGateWayUpdateOrganizationInput:
    """Organization to update Kili API Gateway input."""

    license: Optional[dict] = None  # noqa: A003
    name: Optional[str] = None
