"""Asset domain."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, NewType, Optional

from kili.domain.types import ListOrTuple

if TYPE_CHECKING:
    from kili.domain.issue import IssueStatus, IssueType
    from kili.domain.label import LabelType
    from kili.domain.project import ProjectId

AssetId = NewType("AssetId", str)
AssetExternalId = NewType("AssetExternalId", str)


AssetStatus = Literal["TODO", "ONGOING", "LABELED", "REVIEWED", "TO_REVIEW"]


@dataclass
class AssetFilters:
    """Asset filters for running an asset search."""

    # pylint: disable=too-many-instance-attributes
    project_id: "ProjectId"
    asset_id: Optional[AssetId] = None
    asset_id_in: Optional[ListOrTuple[AssetId]] = None
    asset_id_not_in: Optional[ListOrTuple[AssetId]] = None
    consensus_mark_gte: Optional[float] = None
    consensus_mark_lte: Optional[float] = None
    external_id_strictly_in: Optional[ListOrTuple[AssetExternalId]] = None
    external_id_in: Optional[ListOrTuple[AssetExternalId]] = None
    honeypot_mark_gte: Optional[float] = None
    honeypot_mark_lte: Optional[float] = None
    label_author_in: Optional[ListOrTuple[str]] = None
    label_consensus_mark_gte: Optional[float] = None
    label_consensus_mark_lte: Optional[float] = None
    label_created_at: Optional[str] = None
    label_created_at_gte: Optional[str] = None
    label_created_at_lte: Optional[str] = None
    label_honeypot_mark_gte: Optional[float] = None
    label_honeypot_mark_lte: Optional[float] = None
    label_type_in: Optional[ListOrTuple["LabelType"]] = None
    label_reviewer_in: Optional[ListOrTuple[str]] = None
    metadata_where: Optional[dict] = None
    skipped: Optional[bool] = None
    status_in: Optional[ListOrTuple[AssetStatus]] = None
    updated_at_gte: Optional[str] = None
    updated_at_lte: Optional[str] = None
    label_category_search: Optional[str] = None
    created_at_gte: Optional[str] = None
    created_at_lte: Optional[str] = None
    inference_mark_gte: Optional[float] = None
    inference_mark_lte: Optional[float] = None
    issue_type: Optional["IssueType"] = None
    issue_status: Optional["IssueStatus"] = None
