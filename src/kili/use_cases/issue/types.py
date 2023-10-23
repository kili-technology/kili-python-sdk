"""Types for Issue-related use cases."""

from dataclasses import dataclass
from typing import Optional

from kili.domain.label import LabelId


@dataclass
class IssueToCreateUseCaseInput:
    """Data about one Issue to create."""

    label_id: LabelId
    object_mid: Optional[str] = None
    text: Optional[str] = None
