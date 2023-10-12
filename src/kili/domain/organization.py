"""Organization domain."""
from typing import NewType

OrganizationId = NewType("OrganizationId", str)

Organization = NewType("Organization", dict)
