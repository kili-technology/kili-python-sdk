"""Label domain."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, NewType, Optional

from kili.domain.types import ListOrTuple

if TYPE_CHECKING:
    from .asset import AssetFilters
    from .project import ProjectId
    from .user import UserFilter

LabelId = NewType("LabelId", str)


LabelType = Literal["AUTOSAVE", "DEFAULT", "INFERENCE", "PREDICTION", "REVIEW"]


@dataclass
class LabelFilters:
    """Label filters for running a label search."""

    project_id: "ProjectId"
    asset: Optional["AssetFilters"] = None
    author_in: Optional[ListOrTuple[str]] = None
    consensus_mark_gte: Optional[float] = None
    consensus_mark_lte: Optional[float] = None
    created_at: Optional[str] = None
    created_at_gte: Optional[str] = None
    created_at_lte: Optional[str] = None
    honeypot_mark_gte: Optional[float] = None
    honeypot_mark_lte: Optional[float] = None
    id: Optional[LabelId] = None
    id_in: Optional[ListOrTuple[LabelId]] = None
    labeler_in: Optional[ListOrTuple[str]] = None
    reviewer_in: Optional[ListOrTuple[str]] = None
    search: Optional[str] = None
    type_in: Optional[ListOrTuple[LabelType]] = None
    user: Optional["UserFilter"] = None
