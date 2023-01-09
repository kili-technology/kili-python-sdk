"""
Label mutations
"""

import warnings
from json import dumps
from typing import Dict, List, Optional

from typeguard import typechecked

from kili import services
from kili.enums import LabelType
from kili.helpers import deprecate, format_result
from kili.mutations.helpers import check_asset_identifier_arguments
from kili.mutations.label.queries import (
    GQL_APPEND_TO_LABELS,
    GQL_CREATE_HONEYPOT,
    GQL_UPDATE_PROPERTIES_IN_LABEL,
)
from kili.orm import Label
from kili.services.helpers import (
    assert_all_arrays_have_same_size,
    infer_ids_from_external_ids,
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

    @typechecked
    def create_predictions(
        self,
        project_id: str,
        external_id_array: Optional[List[str]] = None,
        model_name_array: Optional[List[str]] = None,
        json_response_array: Optional[List[dict]] = None,
        model_name: Optional[str] = None,
        asset_id_array: Optional[List[str]] = None,
    ) -> dict:
        # pylint: disable=line-too-long
        """Create predictions for specific assets.

        Args:
            project_id: Identifier of the project.
            external_id_array: The external IDs of the assets for which we want to add predictions.
            model_name_array: In case you want to precise from which model the label originated.
            json_response_array: The predictions are given here. For examples,
                see [the recipe](https://docs.kili-technology.com/recipes/importing-labels-and-predictions).
            asset_id_array: The internal IDs of the assets for which we want to add predictions.

        Returns:
            A result object which indicates if the mutation was successful, or an error message.

        !!! example "Recipe"
            For more detailed examples on how to create predictions, see [the recipe](https://docs.kili-technology.com/recipes/importing-labels-and-predictions).
        """
        if json_response_array is None or len(json_response_array) == 0:
            raise ValueError(
                "json_response_array is empty, you must provide at least one prediction to upload"
            )
        assert_all_arrays_have_same_size(
            [external_id_array, json_response_array, model_name_array, asset_id_array]
        )
        if model_name is None:
            if model_name_array is None:
                raise ValueError("You must provide a model name with the model_name argument ")
            if len(set(model_name_array)) > 1:
                raise ValueError(
                    "Creating predictions from different models is not supported anymore. Separate"
                    " your calls by models."
                )
            warnings.warn(
                "The use of `model_name_array` is deprecated. Creating predictions from different"
                " models is not supported anymore. Please use `model_name` argument instead to"
                " provide the predictions model name.",
                DeprecationWarning,
            )
            model_name = model_name_array[0]

        labels = [
            {
                "asset_id": asset_id,
                "asset_external_id": asset_external_id,
                "json_response": json_response,
            }
            for (asset_id, asset_external_id, json_response) in list(
                zip(
                    asset_id_array or [None] * len(json_response_array),
                    external_id_array or [None] * len(json_response_array),
                    json_response_array,
                )
            )
        ]
        services.import_labels_from_dict(self, project_id, labels, "PREDICTION", model_name)
        return {"id": project_id}

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
        check_asset_identifier_arguments(
            project_id,
            [label_asset_id] if label_asset_id else None,
            [label_asset_external_id] if label_asset_external_id else None,
        )
        if label_asset_id is None:
            assert label_asset_external_id and project_id
            label_asset_id = infer_ids_from_external_ids(
                self, [label_asset_external_id], project_id
            )[label_asset_external_id]
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
    def append_labels(  # pylint: disable=dangerous-default-value
        self,
        asset_id_array: Optional[List[str]] = None,
        json_response_array: List[Dict] = [],
        author_id_array: Optional[List[str]] = None,
        seconds_to_label_array: Optional[List[int]] = None,
        model_name: Optional[str] = None,
        label_type: LabelType = "DEFAULT",
        project_id: Optional[str] = None,
        asset_external_id_array: Optional[List[str]] = None,
        disable_tqdm: bool = False,
    ) -> List:
        """Append labels to assets.

        Args:
            asset_id_array: list of asset internal ids to append labels on
            json_response_array: list of labels to append
            author_id_array: list of the author id of the labels
            seconds_to_label_array: list of times taken to produce the label, in seconds
            model_name: Only useful when uploading predictions.
                Name of the model when uploading predictions
            label_type: Can be one of `AUTOSAVE`, `DEFAULT`, `PREDICTION`, `REVIEW` or `INFERENCE`
            project_id: Identifier of the project
            asset_external_id_array: list of asset external ids to append labels on

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.

        Examples:
            >>> kili.append_to_labels(
                    asset_id_array=['cl9wmlkuc00050qsz6ut39g8h', 'cl9wmlkuw00080qsz2kqh8aiy'],
                    json_response_array=[{...}, {...}]
                )
        """
        if len(json_response_array) == 0:
            raise ValueError(
                "json_response_array is empty, you must provide at least one label to upload"
            )
        check_asset_identifier_arguments(project_id, asset_id_array, asset_external_id_array)
        assert_all_arrays_have_same_size(
            [
                seconds_to_label_array,
                author_id_array,
                json_response_array,
                asset_external_id_array,
                asset_id_array,
            ]
        )

        labels = [
            {
                "asset_id": asset_id,
                "asset_external_id": asset_external_id,
                "json_response": json_response,
                "seconds_to_label": seconds_to_label,
                "author_id": author_id,
            }
            for (asset_id, asset_external_id, json_response, seconds_to_label, author_id,) in list(
                zip(
                    asset_id_array or [None] * len(json_response_array),
                    asset_external_id_array or [None] * len(json_response_array),
                    json_response_array,
                    seconds_to_label_array or [None] * len(json_response_array),
                    author_id_array or [None] * len(json_response_array),
                )
            )
        ]
        return services.import_labels_from_dict(
            self, project_id, labels, label_type, model_name, disable_tqdm
        )

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
        if asset_id is None:
            if asset_external_id is None or project_id is None:
                raise Exception("Either provide asset_id or external_id and project_id")
            asset_id = infer_ids_from_external_ids(self, [asset_external_id], project_id)[
                asset_external_id
            ]

        variables = {
            "data": {"jsonResponse": dumps(json_response)},
            "where": {"id": asset_id},
        }
        result = self.auth.client.execute(GQL_CREATE_HONEYPOT, variables)
        return format_result("data", result, Label)
