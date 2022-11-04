"""
Types for the label mutations
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Extra, validator


class LabelData(BaseModel, extra=Extra.forbid):
    """
    Data about a label to append
    """

    asset_id: str
    json_response: Dict
    author_id: Optional[str]
    seconds_to_label: Optional[int]
    modelName: Optional[str]


class LabelsValidator(BaseModel, extra=Extra.forbid):
    """
    Data about a label to append
    """

    labels: List[Dict]

    @validator("labels", each_item=True)
    def label_validator(cls, label):  # pylint: disable=no-self-argument
        return LabelData(**label)
