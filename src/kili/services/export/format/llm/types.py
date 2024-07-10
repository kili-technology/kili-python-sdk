"""Custom Types."""

from enum import Enum
from typing import List, Optional, TypedDict


class ExportLLMItem(TypedDict):
    """LLM asset chat part."""

    role: str
    content: str
    id: Optional[str]
    chat_id: Optional[str]
    model: Optional[str]


class ExportLLMAsset(TypedDict):
    """LLM export asset format."""

    raw_data: List[ExportLLMItem]


class RankingValue(str, Enum):
    """Possible value for ranking."""

    A_3 = "A_3"
    A_2 = "A_2"
    A_1 = "A_1"
    TIE = "TIE"
    B_1 = "B_1"
    B_2 = "B_2"
    B_3 = "B_3"
