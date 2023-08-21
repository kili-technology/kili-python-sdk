"""Types for the Issue-related graphql gateway functions."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class IssueToCreateGQLGatewayInput:
    """Data about an issue to create needed in graphql createIssue resolver."""

    issue_number: int
    label_id: Optional[str]
    object_mid: Optional[str]
    asset_id: str
    text: Optional[str]
