"""
Types specific to import
"""
from typing import Dict, NewType, Optional

from typing_extensions import NotRequired, TypedDict

from kili.services.types import LabelType

Classes = NewType("Classes", Dict[int, str])


class LabelToImport(TypedDict):
    """
    Typed dictionary that specifies the keys and types for the labels to import.
    """

    author_id: NotRequired[str]
    label_asset_external_id: NotRequired[Optional[str]]
    label_asset_id: NotRequired[Optional[str]]
    label_type: NotRequired[Optional[LabelType]]
    seconds_to_label: NotRequired[Optional[int]]
    path: str
