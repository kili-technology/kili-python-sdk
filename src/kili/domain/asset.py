"""Asset domain."""
from dataclasses import dataclass
from typing import List, NewType, Optional

from kili.domain.issue import IssueStatus, IssueType

AssetId = NewType("AssetId", str)
AssetExternalId = NewType("AssetExternalId", str)


@dataclass
class AssetFilters:
    """Asset filters for running an asset search."""

    # pylint: disable=too-many-instance-attributes
    project_id: str
    asset_id: Optional[str] = None
    asset_id_in: Optional[List[str]] = None
    asset_id_not_in: Optional[List[str]] = None
    consensus_mark_gte: Optional[float] = None
    consensus_mark_lte: Optional[float] = None
    external_id_strictly_in: Optional[List[str]] = None
    external_id_in: Optional[List[str]] = None
    honeypot_mark_gte: Optional[float] = None
    honeypot_mark_lte: Optional[float] = None
    label_author_in: Optional[List[str]] = None
    label_consensus_mark_gte: Optional[float] = None
    label_consensus_mark_lte: Optional[float] = None
    label_created_at: Optional[str] = None
    label_created_at_gte: Optional[str] = None
    label_created_at_lte: Optional[str] = None
    label_honeypot_mark_gte: Optional[float] = None
    label_honeypot_mark_lte: Optional[float] = None
    label_type_in: Optional[List[str]] = None
    label_reviewer_in: Optional[List[str]] = None
    metadata_where: Optional[dict] = None
    skipped: Optional[bool] = None
    status_in: Optional[List[str]] = None
    updated_at_gte: Optional[str] = None
    updated_at_lte: Optional[str] = None
    label_category_search: Optional[str] = None
    created_at_gte: Optional[str] = None
    created_at_lte: Optional[str] = None
    inference_mark_gte: Optional[float] = None
    inference_mark_lte: Optional[float] = None
    issue_type: Optional[IssueType] = None
    issue_status: Optional[IssueStatus] = None
