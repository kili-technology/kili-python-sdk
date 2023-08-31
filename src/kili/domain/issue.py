"""Issue domain."""
from dataclasses import dataclass
from typing import List, Literal, Optional

IssueType = Literal["ISSUE", "QUESTION"]
IssueStatus = Literal["OPEN", "SOLVED"]


@dataclass
class Issue:
    """Issue Entity."""

    id_: str


@dataclass
class IssueFilters:
    """Issue filters for running an issue search."""

    project_id: str
    asset_id: Optional[str] = None
    asset_id_in: Optional[List[str]] = None
    issue_type: Optional[IssueType] = None
    status: Optional[IssueStatus] = None
