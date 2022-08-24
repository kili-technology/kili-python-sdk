"""
Label mutations
"""

import warnings
from json import dumps
from typing import List, Optional

from typeguard import typechecked

from ...helpers import Compatible, format_result, infer_id_from_external_id
from ...orm import Label
from ...utils.pagination import _mutate_from_paginated_call
from .queries import (
    GQL_APPEND_TO_LABELS,
    GQL_CREATE_HONEYPOT,
    GQL_CREATE_PREDICTIONS,
    GQL_UPDATE_PROPERTIES_IN_LABEL,
)


class MutationsLabel:
    """Set of Label mutations."""

    # pylint: disable=too-many-arguments,too-many-locals

    def __init__(self, auth):
        """Initializes the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    @Compatible(["v1", "v2"])
    @typechecked
    def create_predictions(
        self,
        project_id: str,
        external_id_array: List[str],
        model_name_array: List[str],
        json_response_array: List[dict],
    ):
        # pylint: disable=line-too-long
        """Create predictions for specific assets.

        Args:
            project_id: Identifier of the project
            external_id_array: The external identifiers of the assets for which we want to add predictions
            model_name_array: In case you want to precise from which model the label originated
            json_response_array: The predictions are given here. For examples,
                see [the recipe](https://github.com/kili-technology/kili-python-sdk/blob/master/recipes/import_predictions.ipynb).

        Returns:
            A result object which indicates if the mutation was successful, or an error message.

        !!! example "Recipe"
            For more detailed examples on how to create predictions, see [the recipe](https://github.com/kili-technology/kili-python-sdk/blob/master/recipes/import_predictions.ipynb).
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
            self, properties_to_batch, generate_variables, GQL_CREATE_PREDICTIONS
        )
        return format_result("data", results[0], Label)

    @Compatible(["v1", "v2"])
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
        """Append a label to an asset.

        Args:
            json_response: Label is given here
            author_id: ID of the author of the label
            label_asset_external_id: External identifier of the asset
            label_asset_id: Identifier of the asset
            project_id: Identifier of the project
            label_type: Can be one of `AUTOSAVE`, `DEFAULT`, `PREDICTION` or `REVIEW`
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
                "skipped": False,  # this is a deprecated field but kept here for compatibility
                # with deployed backends.
            },
            "where": {"id": label_asset_id},
        }
        result = self.auth.client.execute(GQL_APPEND_TO_LABELS, variables)
        return format_result("data", result, Label)

    @Compatible(["v1", "v2"])
    @typechecked
    def update_properties_in_label(
        self,
        label_id: str,
        seconds_to_label: Optional[int] = None,
        model_name: Optional[str] = None,
        json_response: Optional[dict] = None,
    ):
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

    @Compatible(["v1", "v2"])
    @typechecked
    def create_honeypot(
        self,
        json_response: dict,
        asset_external_id: Optional[str] = None,
        asset_id: Optional[str] = None,
        project_id: Optional[str] = None,
    ):
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
