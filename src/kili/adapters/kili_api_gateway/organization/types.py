"""Organization types for Kili API Gateway."""
from dataclasses import dataclass


@dataclass(frozen=True)
class KiliAPIGateWayCreateOrganizationInput:
    """Organization to create Kili API Gateway input."""

    name: str
    address: str
    city: str
    country: str
    zip_code: str
