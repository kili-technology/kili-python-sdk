"""Types for label-related use cases."""

from dataclasses import dataclass
from typing import Dict, Optional

from kili.domain.asset import AssetExternalId, AssetId
from kili.domain.label import LabelType
from kili.domain.user import UserId


@dataclass
class LabelToCreateUseCaseInput:
    """Data about one label to create."""

    asset_id: Optional[AssetId]
    asset_external_id: Optional[AssetExternalId]
    label_type: LabelType
    json_response: Dict
    author_id: Optional[UserId]
    seconds_to_label: Optional[float]
    model_name: Optional[str]
