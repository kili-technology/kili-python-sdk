"""Gateway types for questions."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class QuestionsToCreateGatewayInput:
    """Questions to create gateway input."""

    asset_id: Optional[str] = None
    text: Optional[str] = None
    external_id: Optional[str] = None
