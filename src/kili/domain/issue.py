"""Issue domain."""

from dataclasses import dataclass
from typing import List, Literal, NewType, Optional

from kili.domain.project import ProjectId

IssueType = Literal["ISSUE", "QUESTION"]
IssueStatus = Literal["OPEN", "SOLVED"]
IssueId = NewType("IssueId", str)


@dataclass
class IssueFilters:
    """Issue filters for running an issue search."""

    project_id: ProjectId
    asset_id: Optional[str] = None
    asset_id_in: Optional[List[str]] = None
    issue_type: Optional[IssueType] = None
    status: Optional[IssueStatus] = None
