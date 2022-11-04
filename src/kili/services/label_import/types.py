"""
Types specific to import
"""
from typing import Dict, List, NewType, Optional

from pydantic import BaseModel, Extra, validator
from typing_extensions import Literal, Required, TypedDict

from kili.services.types import LabelType

Classes = NewType("Classes", Dict[int, str])
LabelFormat = Literal["yolo_v4", "yolo_v5", "yolo_v7", "raw"]


class LabelToImport(TypedDict, total=False):
    """
    Typed dictionary that specifies the keys and types for the labels to import.
    """

    author_id: str
    label_asset_external_id: Optional[str]
    label_asset_id: Optional[str]
    label_type: Optional[LabelType]
    seconds_to_label: Optional[int]
    path: Required[str]


class LabelData(BaseModel, extra=Extra.forbid):
    """
    Data about a label to append
    """

    asset_id: str
    json_response: Dict
    author_id: Optional[str]
    seconds_to_label: Optional[int]
    model_name: Optional[str]


class LabelsValidator(BaseModel, extra=Extra.forbid):
    """
    Data about a label to append
    """

    labels: List[Dict]

    @validator("labels", each_item=True)
    def label_validator(cls, label):  # pylint: disable=no-self-argument
        return LabelData(**label)
