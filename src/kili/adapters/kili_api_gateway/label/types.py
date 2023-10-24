"""Types for the label-related Kili API gateway functions."""

from dataclasses import dataclass
from typing import Dict, List, Optional

from kili.domain.asset import AssetId
from kili.domain.label import LabelId, LabelType
from kili.domain.user import UserId


@dataclass
class UpdateLabelData:
    """LabelData data."""

    is_sent_back_to_queue: Optional[bool]
    json_response: Optional[Dict]
    model_name: Optional[str]
    seconds_to_label: Optional[float]


@dataclass
class ReviewedLabelData:
    """ReviewedLabelData data."""

    id: LabelId  # noqa: A003


@dataclass
class AppendLabelData:
    """AppendLabelData data."""

    author_id: Optional[UserId]
    asset_id: AssetId
    client_version: Optional[int]
    json_response: Dict
    seconds_to_label: Optional[float]
    model_name: Optional[str]
    reviewed_label: Optional[ReviewedLabelData]


@dataclass
class AppendManyLabelsData:
    """AppendManyLabelsData data."""

    labels_data: List[AppendLabelData]
    label_type: LabelType
    refuse_invalid_json_response: Optional[bool]
    overwrite: Optional[bool]
