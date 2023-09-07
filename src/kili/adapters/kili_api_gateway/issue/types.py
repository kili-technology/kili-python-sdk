"""Types for the Issue-related Kili API gateway functions."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class IssueToCreateKiliAPIGatewayInput:
    """Data about an issue to create needed in graphql createIssue resolver."""

    label_id: str
    object_mid: Optional[str]
    text: Optional[str]
