"""Types for label-related use cases."""

from dataclasses import dataclass
from typing import Dict, Optional

from kili.domain.asset import AssetExternalId, AssetId
from kili.domain.label import LabelType
from kili.domain.user import UserId


@dataclass
class LabelToCreateUseCaseInput:
    """Data about one label to create."""

    asset_external_id: Optional[AssetExternalId]
    asset_id: Optional[AssetId]
    author_id: Optional[UserId]
    json_response: Dict
    label_type: LabelType
    model_name: Optional[str]
    referenced_label_id: Optional[str]
    seconds_to_label: Optional[float]
