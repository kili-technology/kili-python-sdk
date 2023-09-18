"""Types specific to import."""
from typing import Dict, List, Literal, NewType

from typeguard import typechecked

Classes = NewType("Classes", Dict[int, str])
LabelFormat = Literal["yolo_v4", "yolo_v5", "yolo_v7", "kili", "raw"]


@typechecked
def check_input_labels(labels: List[Dict]) -> None:
    """Check that input labels are valid."""
    for label in labels:
        check_input_label(label)

    is_using_asset_id = labels[0].get("asset_id") is not None
    if is_using_asset_id and not all(label.get("asset_id") for label in labels):
        raise ValueError(
            "Please use the same asset identifier for all labels: either only `asset_id` or"
            " only `asset_external_id`."
        )


MANDATORY_LABEL_KEYS_TYPES = {
    "json_response": Dict,
}

OPTIONAL_LABEL_KEYS_TYPES = {
    "asset_id": str,
    "asset_external_id": str,
    "author_id": str,
    "seconds_to_label": int,
}

VALID_KEYS = set(MANDATORY_LABEL_KEYS_TYPES.keys()).union(OPTIONAL_LABEL_KEYS_TYPES.keys())


@typechecked
def check_input_label(label: Dict) -> None:
    """Check that input label is valid."""
    if label.get("asset_external_id") is None and label.get("asset_id") is None:
        raise ValueError("You must either provide the `asset_id` or `external_id`.")

    for key in label:
        if key not in VALID_KEYS:
            raise ValueError(f"The `{key}` key is not a valid key.")

    for key, expected_type in MANDATORY_LABEL_KEYS_TYPES.items():
        if key not in label:
            raise ValueError(f"The `{key}` key is mandatory.")

        if not isinstance(label[key], expected_type):
            raise TypeError(f"The `{key}` field must be of type `{expected_type}`.")

    for key, expected_type in OPTIONAL_LABEL_KEYS_TYPES.items():
        if label.get(key) is not None and not isinstance(label[key], expected_type):
            raise TypeError(f"The `{key}` field must be of type `{expected_type}`.")
