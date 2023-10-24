"""Label mutations."""

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
from kili.entrypoints.mutations.label.queries import GQL_APPEND_TO_LABELS
from kili.use_cases.asset.utils import AssetUseCasesUtils
from kili.utils.logcontext import for_all_methods, log_call


@for_all_methods(log_call, exclude=["__init__"])
class MutationsLabel(BaseOperationEntrypointMixin):
    """Set of Label mutations."""

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
