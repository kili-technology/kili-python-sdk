"""Types for Issue-related use cases."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class IssueToCreateUseCaseInput:
    """Data about one Issue to create."""

    label_id: str
    object_mid: Optional[str] = None
    text: Optional[str] = None
