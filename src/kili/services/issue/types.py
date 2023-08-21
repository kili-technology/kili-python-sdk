"""Types for Issue-related service."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class IssueToCreateServiceInput:
    """Data about one Issue to create."""

    label_id: str
    object_mid: Optional[str] = None
    text: Optional[str] = None
