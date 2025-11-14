"""Types for the label-related Kili API gateway functions."""

from dataclasses import dataclass
from typing import Dict, List, Optional

from kili.domain.asset import AssetId
from kili.domain.label import LabelType
from kili.domain.user import UserId


@dataclass
class UpdateLabelData:
    """Data to update a label."""

    is_sent_back_to_queue: Optional[bool]
    json_response: Optional[Dict]
    model_name: Optional[str]
    seconds_to_label: Optional[float]


@dataclass
class AppendLabelData:
    """AppendLabelData data."""

    asset_id: AssetId
    author_id: Optional[UserId]
    client_version: Optional[int]
    json_response: Dict
    model_name: Optional[str]
    referenced_label_id: Optional[str]
    seconds_to_label: Optional[float]


@dataclass
class AppendManyLabelsData:
    """AppendManyLabelsData data."""

    labels_data: List[AppendLabelData]
    label_type: LabelType
    overwrite: Optional[bool]
    step_name: Optional[str] = None


@dataclass
class AppendToLabelsData:
    """AppendToLabelsData graphql input."""

    author_id: UserId
    client_version: Optional[int]
    json_response: Dict
    label_type: LabelType
    seconds_to_label: Optional[float]
    skipped: Optional[bool]
