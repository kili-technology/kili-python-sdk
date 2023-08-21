"""Issue domain."""
from dataclasses import dataclass
from typing import Literal

IssueType = Literal["ISSUE", "QUESTION"]
IssueStatus = Literal["OPEN", "SOLVED"]


@dataclass
class Issue:
    """Issue Entity."""

    id_: str
