"""Types for the Issue-related Kili API gateway functions."""
from dataclasses import dataclass
from typing import List, Optional

from kili.domain.issue import IssueStatus, IssueType


@dataclass
class IssueToCreateKiliAPIGatewayInput:
    """Data about an issue to create needed in graphql createIssue resolver."""

    label_id: Optional[str]
    object_mid: Optional[str]
    asset_id: str
    text: Optional[str]


@dataclass
class IssueWhere:
    """Tuple to be passed to the IssueQuery to restrict query."""

    project_id: str
    asset_id: Optional[str] = None
    asset_id_in: Optional[List[str]] = None
    issue_type: Optional[IssueType] = None
    status: Optional[IssueStatus] = None

    def get_graphql_where_value(self):
        """Build the GraphQL IssueWhere variable value to be sent in an operation."""
        return {
            "project": {"id": self.project_id},
            "asset": {"id": self.asset_id},
            "assetIn": self.asset_id_in,
            "status": self.status,
            "type": self.issue_type,
        }
