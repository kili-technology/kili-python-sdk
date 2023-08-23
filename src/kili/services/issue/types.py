"""Types for Issue-related service."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class IssueToCreateServiceInput:
    """Data about one Issue to create."""

    label_id: str
    object_mid: Optional[str] = None
    text: Optional[str] = None


@dataclass
class QuestionToCreateServiceInput:
    """Data about one Issue to create."""

    asset_id: Optional[str]
    asset_external_id: Optional[str]
    text: str
