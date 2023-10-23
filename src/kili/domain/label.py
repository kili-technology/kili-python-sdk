"""Label domain."""

from dataclasses import dataclass
from typing import List, Literal, NewType, Optional

from .asset import AssetFilters
from .project import ProjectFilters
from .user import UserFilter

LabelId = NewType("LabelId", str)

LabelType = Literal["AUTOSAVE", "DEFAULT", "INFERENCE", "PREDICTION", "REVIEW"]


@dataclass
class LabelFilters:
    """Label filters for running a label search."""

    asset: Optional[AssetFilters]
    author_in: Optional[List[str]]
    consensus_mark_gte: Optional[float]
    consensus_mark_lte: Optional[float]
    created_at: Optional[str]
    created_at_gte: Optional[str]
    created_at_lte: Optional[str]
    honeypot_mark_gte: Optional[float]
    honeypot_mark_lte: Optional[float]
    id: Optional[LabelId]  # noqa: A003
    id_in: Optional[List[LabelId]]
    labeler_in: Optional[List[str]]
    project: Optional[ProjectFilters]
    reviewer_in: Optional[List[str]]
    search: Optional[str]
    type_in: Optional[List[str]]
    user: Optional[UserFilter]
