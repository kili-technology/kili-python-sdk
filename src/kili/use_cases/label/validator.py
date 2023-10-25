"""Validator for import of labels."""

from typing import List

from typeguard import typechecked

from .types import LabelToCreateUseCaseInput


@typechecked
def check_input_labels(labels: List[LabelToCreateUseCaseInput]) -> None:
    """Check that input labels are valid."""
    for label in labels:
        _check_input_label(label)

    is_using_asset_id = labels[0].asset_id is not None
    if is_using_asset_id and not all(label.asset_id for label in labels):
        raise ValueError(
            "Please use the same asset identifier for all labels: either only `asset_id` or"
            " only `asset_external_id`."
        )


@typechecked
def _check_input_label(label: LabelToCreateUseCaseInput) -> None:
    """Check that a single input label is valid."""
    if label.asset_external_id is None and label.asset_id is None:
        raise ValueError("You must either provide the `asset_id` or the `external_id`.")

    if label.label_type == "PREDICTION" and not label.model_name:
        raise ValueError("You must provide `model_name` when uploading `PREDICTION` labels.")
