"""Types specific to import."""
from typing import Dict, List, Literal, NewType, Optional

from pydantic import BaseModel, StrictInt, StrictStr, field_validator

Classes = NewType("Classes", Dict[int, str])
LabelFormat = Literal["yolo_v4", "yolo_v5", "yolo_v7", "kili", "raw"]


class ClientInputLabelData(BaseModel, extra="forbid"):
    """Data about a label to append, given by client in client-side function."""

    asset_id: Optional[StrictStr] = None
    asset_external_id: Optional[StrictStr] = None
    json_response: dict
    author_id: Optional[StrictStr] = None
    seconds_to_label: Optional[StrictInt] = None


class ClientInputLabelsValidator(BaseModel, extra="forbid"):
    """Validates the data about a label to append."""

    labels: List[Dict]

    @field_validator("labels")
    @classmethod
    def label_validator(cls, labels: List[Dict]) -> List[Dict]:
        """Validate the data of one label."""
        for i, _ in enumerate(labels):
            if labels[i].get("asset_external_id") is None and labels[i].get("asset_id") is None:
                raise ValueError("You must either provide the `asset_id` or `external_id`.")
            labels[i] = ClientInputLabelData(**labels[i]).model_dump()
        return labels

    @field_validator("labels")
    @classmethod
    def all_labels_use_the_same_asset_identifier(cls, labels: List[Dict]) -> List[Dict]:
        """Validate the data of all labels."""
        if not all(label.get("asset_id") for label in labels) and not all(
            label.get("asset_external_id") for label in labels
        ):
            raise ValueError(
                "Please use the same asset identifier for all labels: either only `asset_id` or"
                " only `asset_external_id`."
            )
        return labels
