"""Gateway types for questions."""
from dataclasses import dataclass
from typing import Optional

from kili.domain.asset import AssetExternalId, AssetId


@dataclass
class QuestionsToCreateGatewayInput:
    """Questions to create gateway input."""

    asset_id: Optional[AssetId] = None
    text: Optional[str] = None
    external_id: Optional[AssetExternalId] = None
