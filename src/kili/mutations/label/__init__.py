"""
Label mutations
"""

import warnings
from itertools import repeat
from json import dumps
from typing import Dict, List, Optional

from typeguard import typechecked

from kili.enums import LabelType
from kili.helpers import deprecate, format_result, infer_id_from_external_id
from kili.mutations.label.queries import (
    GQL_APPEND_TO_LABELS,
    GQL_CREATE_HONEYPOT,
    GQL_CREATE_PREDICTIONS,
    GQL_UPDATE_PROPERTIES_IN_LABEL,
)
from kili.orm import Label
from kili.services.label_import import import_labels_from_dict
from kili.utils.pagination import _mutate_from_paginated_call


class MutationsLabel:
    """Set of Label mutations."""

    # pylint: disable=too-many-arguments,too-many-locals

    def __init__(self, auth):
        """Initializes the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    @typechecked
    def create_predictions(
        self,
        project_id: str,
        external_id_array: List[str],
        model_name_array: List[str],
        json_response_array: List[dict],
    ) -> Label:
        # pylint: disable=line-too-long
        """Create predictions for specific assets.

        Args:
            project_id: Identifier of the project
            external_id_array: The external identifiers of the assets for which we want to add predictions
            model_name_array: In case you want to precise from which model the label originated
            json_response_array: The predictions are given here. For examples,
                see [the recipe](https://docs.kili-technology.com/recipes/importing-labels-and-predictions).

        Returns:
            A result object which indicates if the mutation was successful, or an error message.

        !!! example "Recipe"
            For more detailed examples on how to create predictions, see [the recipe](https://docs.kili-technology.com/recipes/importing-labels-and-predictions).
        """
        assert len(external_id_array) == len(
            json_response_array
        ), "IDs list and predictions list should have the same length"
        assert len(external_id_array) == len(
            model_name_array
        ), "IDs list and model names list should have the same length"
        if len(external_id_array) == 0:
            warnings.warn("Empty IDs and prediction list")

        properties_to_batch = {
            "external_id_array": external_id_array,
            "model_name_array": model_name_array,
            "json_response_array": json_response_array,
        }

        def generate_variables(batch):
            return {
                "data": {
                    "modelNameArray": batch["model_name_array"],
                    "jsonResponseArray": [dumps(elem) for elem in batch["json_response_array"]],
                },
                "where": {
                    "externalIdStrictlyIn": batch["external_id_array"],
                    "project": {"id": project_id},
                },
            }

        results = _mutate_from_paginated_call(
            self,
            properties_to_batch,
            generate_variables,
            GQL_CREATE_PREDICTIONS,
        )
        return format_result("data", results[0], Label)

    @deprecate(
        msg=(
            "append_to_labels method is deprecated. Please use append_labels instead. This new"
            " function allows to import several labels 10 times faster."
        )
    )
    @typechecked
    def append_to_labels(
        self,
        json_response: dict,
        author_id: Optional[str] = None,
        label_asset_external_id: Optional[str] = None,
        label_asset_id: Optional[str] = None,
        label_type: str = "DEFAULT",
        project_id: Optional[str] = None,
        seconds_to_label: Optional[int] = 0,
    ):
        """
        !!! danger "[DEPRECATED]"
            append_to_labels method is deprecated. Please use append_labels instead.
            This new function allows to import several labels 10 times faster.

        Append a label to an asset.

        Args:
            json_response: Label is given here
            author_id: ID of the author of the label
            label_asset_external_id: External identifier of the asset
            label_asset_id: Identifier of the asset
            project_id: Identifier of the project
            label_type: Can be one of `DEFAULT`, `PREDICTION`, `REVIEW` or `INFERENCE`
            seconds_to_label: Time to create the label

        !!! warning
            Either provide `label_asset_id` or `label_asset_external_id` and `project_id`

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.

        Examples:
            >>> kili.append_to_labels(label_asset_id=asset_id, json_response={...})

        """
        if author_id is None:
            author_id = self.auth.user_id
        label_asset_id = infer_id_from_external_id(
            self, label_asset_id, label_asset_external_id, project_id
        )
        variables = {
            "data": {
                "authorID": author_id,
                "jsonResponse": dumps(json_response),
                "labelType": label_type,
                "secondsToLabel": seconds_to_label,
            },
            "where": {"id": label_asset_id},
        }
        result = self.auth.client.execute(GQL_APPEND_TO_LABELS, variables)
        return format_result("data", result, Label)

    @typechecked
    def append_labels(
        self,
        asset_id_array: List[str],
        json_response_array: List[Dict],
        author_id_array: Optional[List[str]] = None,
        seconds_to_label_array: Optional[List[int]] = None,
        model_name: Optional[str] = None,
        label_type: LabelType = "DEFAULT",
    ) -> List:
        """Append labels to assets.

        Args:
            asset_id_array: list of asset ids to append labels on
            json_response_array: list of labels to append
            author_id_array: list of the author id of the labels
            seconds_to_label_array: list of times taken to produce the label, in seconds
            model_name: Only useful when uploading predictions.
                Name of the model when uploading predictions
            label_type: Can be one of `AUTOSAVE`, `DEFAULT`, `PREDICTION`, `REVIEW` or `INFERENCE`

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.

        Examples:
            >>> kili.append_to_labels(
                    asset_id_array=['cl9wmlkuc00050qsz6ut39g8h', 'cl9wmlkuw00080qsz2kqh8aiy'],
                    json_response_array=[{...}, {...}]
                )
        """
        if label_type == "PREDICTION" and model_name is None:
            raise ValueError("You must provide model_name when uploading predictions")
        if len(asset_id_array) != len(json_response_array):
            raise ValueError("asset_id_array and json_response_array should have the same length")
        for array in [seconds_to_label_array, author_id_array]:
            if array is not None and len(array) != len(asset_id_array):
                raise ValueError("All arrays should have the same length")
        labels = [
            {
                "asset_id": asset_id,
                "json_response": json_response,
                "seconds_to_label": seconds_to_label,
                "model_name": model_name,
                "author_id": author_id,
            }
            for (asset_id, json_response, seconds_to_label, author_id, model_name) in list(
                zip(
                    asset_id_array,
                    json_response_array,
                    seconds_to_label_array or [None] * len(asset_id_array),
                    author_id_array or [None] * len(asset_id_array),
                    repeat(model_name),
                )
            )
        ]
        return import_labels_from_dict(self, labels, label_type)

    @typechecked
    def update_properties_in_label(
        self,
        label_id: str,
        seconds_to_label: Optional[int] = None,
        model_name: Optional[str] = None,
        json_response: Optional[dict] = None,
    ) -> Label:
        """Update properties of a label.

        Args:
            label_id: Identifier of the label
            seconds_to_label: Time to create the label
            model_name: Name of the model
            json_response: The label is given here

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.

        Examples:
            >>> kili.update_properties_in_label(label_id=label_id, json_response={...})
        """
        formatted_json_response = None if json_response is None else dumps(json_response)
        variables = {
            "labelID": label_id,
            "secondsToLabel": seconds_to_label,
            "modelName": model_name,
            "jsonResponse": formatted_json_response,
        }
        result = self.auth.client.execute(GQL_UPDATE_PROPERTIES_IN_LABEL, variables)
        return format_result("data", result, Label)

    @typechecked
    def create_honeypot(
        self,
        json_response: dict,
        asset_external_id: Optional[str] = None,
        asset_id: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> Label:
        """Create honeypot for an asset.

        !!! info
            Uses the given `json_response` to create a `REVIEW` label.
            This enables Kili to compute a`honeypotMark`,
            which measures the similarity between this label and other labels.

        Args:
            json_response: The JSON response of the honeypot label of the asset
            asset_id: Identifier of the asset
                Either provide asset_id or asset_external_id and project_id
            asset_external_id: External identifier of the asset
                Either provide asset_id or asset_external_id and project_id
            project_id: Identifier of the project
                Either provide asset_id or asset_external_id and project_id

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.
        """
        asset_id = infer_id_from_external_id(self, asset_id, asset_external_id, project_id)

        variables = {
            "data": {"jsonResponse": dumps(json_response)},
            "where": {"id": asset_id},
        }
        result = self.auth.client.execute(GQL_CREATE_HONEYPOT, variables)
        return format_result("data", result, Label)
