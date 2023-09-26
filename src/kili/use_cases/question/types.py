from dataclasses import dataclass
from typing import Optional

from kili.domain.asset.asset import AssetExternalId, AssetId


@dataclass
class QuestionToCreateUseCaseInput:
    """Question to create use case input."""

    text: Optional[str]
    asset_id: Optional[AssetId]
    asset_external_id: Optional[AssetExternalId]
