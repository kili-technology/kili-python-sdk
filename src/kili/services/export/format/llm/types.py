"""Custom Types."""

from enum import Enum
from typing import List, TypedDict

from kili_formats.types import ExportLLMItem


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
