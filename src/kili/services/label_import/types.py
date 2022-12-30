"""
Types specific to import
"""
from typing import Dict, List, NewType, Optional

from pydantic import BaseModel, Extra, StrictInt, StrictStr, validator
from typing_extensions import Literal

Classes = NewType("Classes", Dict[int, str])
LabelFormat = Literal["yolo_v4", "yolo_v5", "yolo_v7", "kili", "raw"]


class ClientInputLabelData(BaseModel, extra=Extra.forbid):
    """
    Data about a label to append, given by client in client-side function
    """

    asset_id: Optional[StrictStr]
    asset_external_id: Optional[StrictStr]
    json_response: dict
    author_id: Optional[StrictStr]
    seconds_to_label: Optional[StrictInt]


class _ClientInputLabelsValidator(BaseModel, extra=Extra.forbid):
    """
    Validates the data about a label to append
    """

    labels: List[Dict]

    @validator("labels", each_item=True, pre=True)
    def label_validator(cls, label):  # pylint: disable=no-self-argument
        """Validate the data of one label"""
        if label.get("asset_external_id") is None and label.get("asset_id") is None:
            raise ValueError("You must either provide the asset_id or external_id")
        return ClientInputLabelData(**label)

    @validator("labels")
    def all_labels_use_the_same_asset_identifier(cls, labels):  # pylint: disable=no-self-argument
        """Validate the data of one label"""
        if not all((label.get("asset_id") for label in labels)) and not all(
            (label.get("asset_external_id") for label in labels)
        ):
            raise ValueError(
                "Please use the same asset identifier for all labels: either only asset_id or only"
                " asset_external_id"
            )
        return labels
