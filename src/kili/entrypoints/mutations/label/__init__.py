"""Label mutations."""

import warnings
from json import dumps
from typing import Dict, List, Literal, Optional, cast

from typeguard import typechecked

from kili.core.helpers import deprecate
from kili.domain.asset import AssetExternalId, AssetId
from kili.domain.asset.helpers import check_asset_identifier_arguments
from kili.domain.label import LabelType
from kili.domain.project import ProjectId
from kili.domain.types import ListOrTuple
from kili.entrypoints.base import BaseOperationEntrypointMixin
from kili.entrypoints.mutations.label.queries import (
    GQL_APPEND_TO_LABELS,
    GQL_CREATE_HONEYPOT,
)
from kili.presentation.client.helpers.common_validators import (
    assert_all_arrays_have_same_size,
)
from kili.use_cases.asset.utils import AssetUseCasesUtils
from kili.utils.logcontext import for_all_methods, log_call


@for_all_methods(log_call, exclude=["__init__"])
class MutationsLabel(BaseOperationEntrypointMixin):
    """Set of Label mutations."""

    # pylint: disable=too-many-arguments
    @typechecked
    def create_predictions(
        self,
        project_id: str,
        external_id_array: Optional[List[str]] = None,
        model_name_array: Optional[List[str]] = None,
        json_response_array: Optional[List[dict]] = None,
        model_name: Optional[str] = None,
        asset_id_array: Optional[List[str]] = None,
        disable_tqdm: Optional[bool] = None,
        overwrite: bool = False,
    ) -> Dict[Literal["id"], str]:
        # pylint: disable=line-too-long
        """Create predictions for specific assets.

        Args:
            project_id: Identifier of the project.
            external_id_array: The external IDs of the assets for which we want to add predictions.
            model_name_array: Deprecated, use `model_name` instead.
            json_response_array: The predictions are given here. For examples,
                see [the recipe](https://docs.kili-technology.com/recipes/importing-labels-and-predictions).
            model_name: The name of the model that generated the predictions
            asset_id_array: The internal IDs of the assets for which we want to add predictions.
            disable_tqdm: Disable tqdm progress bar.
            overwrite: if True, it will overwrite existing predictions of
                the same model name on the targeted assets.

        Returns:
            A dictionary with the project `id`.

        !!! example "Recipe"
            For more detailed examples on how to create predictions, see [the recipe](https://docs.kili-technology.com/recipes/importing-labels-and-predictions).

        !!! warning "model name"
            The use of `model_name_array` is deprecated. Creating predictions from different
            models is not supported anymore. Please use `model_name` argument instead to
            provide the predictions model name.
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
                "The use of `model_name_array` is deprecated. Creating predictions from"
                " different models is not supported anymore. Please use `model_name` argument"
                " instead to provide the predictions model name.",
                DeprecationWarning,
                stacklevel=1,
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
        import_labels_from_dict(
            self, project_id, labels, "PREDICTION", overwrite, model_name, disable_tqdm
        )
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
        label_type: LabelType = "DEFAULT",
        project_id: Optional[str] = None,
        seconds_to_label: Optional[int] = 0,
    ) -> Dict[Literal["id"], str]:
        """!!! danger "[DEPRECATED]".

        append_to_labels method is deprecated. Please use append_labels instead.
            This new function allows to import several labels 10 times faster.

        Append a label to an asset.

        Args:
            json_response: Label is given here.
            author_id: ID of the author of the label.
            label_asset_external_id: External identifier of the asset.
            label_asset_id: Identifier of the asset.
            project_id: Identifier of the project.
            label_type: Can be one of `AUTOSAVE`, `DEFAULT`, `PREDICTION`, `REVIEW` or `INFERENCE`.
            seconds_to_label: Time to create the label.

        !!! warning
            Either provide `label_asset_id` or `label_asset_external_id` and `project_id`

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.

        Examples:
            >>> kili.append_to_labels(label_asset_id=asset_id, json_response={...})
        """
        if author_id is None:
            user = self.kili_api_gateway.get_current_user(fields=("id",))
            author_id = user["id"]

        check_asset_identifier_arguments(
            ProjectId(project_id) if project_id else None,
            cast(ListOrTuple[AssetId], [label_asset_id]) if label_asset_id else None,
            (
                cast(ListOrTuple[AssetExternalId], [label_asset_external_id])
                if label_asset_external_id
                else None
            ),
        )
        if (
            label_asset_id is None
            and label_asset_external_id is not None
            and project_id is not None
        ):
            label_asset_id = AssetUseCasesUtils(self.kili_api_gateway).infer_ids_from_external_ids(
                cast(List[AssetExternalId], [label_asset_external_id]), ProjectId(project_id)
            )[AssetExternalId(label_asset_external_id)]
        variables = {
            "data": {
                "authorID": author_id,
                "jsonResponse": dumps(json_response),
                "labelType": label_type,
                "secondsToLabel": seconds_to_label,
            },
            "where": {"id": label_asset_id},
        }
        result = self.graphql_client.execute(GQL_APPEND_TO_LABELS, variables)
        return self.format_result("data", result, None)

    @typechecked
    def create_honeypot(
        self,
        json_response: dict,
        asset_external_id: Optional[str] = None,
        asset_id: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> Dict:
        """Create honeypot for an asset.

        !!! info
            Uses the given `json_response` to create a `REVIEW` label.
            This enables Kili to compute a`honeypotMark`,
            which measures the similarity between this label and other labels.

        Args:
            json_response: The JSON response of the honeypot label of the asset.
            asset_id: Identifier of the asset.
                Either provide `asset_id` or `asset_external_id` and `project_id`.
            asset_external_id: External identifier of the asset.
                Either provide `asset_id` or `asset_external_id` and `project_id`.
            project_id: Identifier of the project.
                Either provide `asset_id` or `asset_external_id` and `project_id`.

        Returns:
            A dictionary-like object representing the created label.
        """
        if asset_id is None:
            if asset_external_id is None or project_id is None:
                raise ValueError(
                    "Either provide `asset_id` or `asset_external_id` and `project_id`."
                )
            asset_id = AssetUseCasesUtils(self.kili_api_gateway).infer_ids_from_external_ids(
                cast(ListOrTuple[AssetExternalId], [asset_external_id]),
                ProjectId(project_id),
            )[AssetExternalId(asset_external_id)]

        variables = {
            "data": {"jsonResponse": dumps(json_response)},
            "where": {"id": asset_id},
        }
        result = self.graphql_client.execute(GQL_CREATE_HONEYPOT, variables)
        return self.format_result("data", result, None)
