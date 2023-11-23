"""Label use cases."""

from functools import partial
from typing import TYPE_CHECKING, Dict, Generator, List, Literal, Optional

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.adapters.kili_api_gateway.label.types import (
    AppendLabelData,
    AppendManyLabelsData,
    AppendToLabelsData,
    UpdateLabelData,
)
from kili.domain.asset import AssetExternalId, AssetFilters, AssetId
from kili.domain.label import LabelFilters, LabelId, LabelType
from kili.domain.project import ProjectId
from kili.domain.types import ListOrTuple
from kili.domain.user import UserId
from kili.use_cases.asset.utils import AssetUseCasesUtils
from kili.use_cases.base import BaseUseCases
from kili.utils.labels.parsing import parse_labels

from .types import LabelToCreateUseCaseInput
from .validator import check_input_labels

if TYPE_CHECKING:
    import pandas as pd


class LabelUseCases(BaseUseCases):
    """Label use cases."""

    def count_labels(self, filters: LabelFilters) -> int:
        """Count labels."""
        return self._kili_api_gateway.count_labels(filters=filters)

    def list_labels(
        self,
        project_id: ProjectId,
        filters: LabelFilters,
        fields: ListOrTuple[str],
        options: QueryOptions,
        output_format: Literal["dict", "parsed_label"],
    ) -> Generator:
        """List labels."""
        label_parser_post_function = None
        if output_format == "parsed_label":
            if "jsonResponse" not in fields:
                raise ValueError(
                    "The field 'jsonResponse' is required to parse labels. Please add it to the"
                    " 'fields' argument."
                )

            project = self._kili_api_gateway.get_project(
                project_id, fields=("jsonInterface", "inputType")
            )

            label_parser_post_function = partial(
                parse_labels,
                json_interface=project["jsonInterface"],
                input_type=project["inputType"],
            )

        labels_gen = self._kili_api_gateway.list_labels(
            fields=fields, filters=filters, options=options
        )

        if label_parser_post_function is not None:
            labels_gen = label_parser_post_function(labels=labels_gen)

        return labels_gen

    def update_properties_in_label(
        self,
        label_id: LabelId,
        seconds_to_label: Optional[int],
        model_name: Optional[str],
        json_response: Optional[Dict],
        fields: ListOrTuple[str],
    ) -> Dict:
        """Update properties in label."""
        return self._kili_api_gateway.update_properties_in_label(
            label_id=label_id,
            data=UpdateLabelData(
                json_response=json_response,
                model_name=model_name,
                seconds_to_label=seconds_to_label,
                is_sent_back_to_queue=None,
            ),
            fields=fields,
        )

    def delete_labels(
        self, ids: ListOrTuple[LabelId], disable_tqdm: Optional[bool]
    ) -> List[LabelId]:
        """Delete labels."""
        return self._kili_api_gateway.delete_labels(ids=ids, disable_tqdm=disable_tqdm)

    def append_labels(
        self,
        labels: List[LabelToCreateUseCaseInput],
        label_type: LabelType,
        overwrite: Optional[bool],
        project_id: Optional[ProjectId],
        fields: ListOrTuple[str],
        disable_tqdm: Optional[bool],
    ) -> List[Dict]:
        """Append labels."""
        check_input_labels(labels)

        asset_id_array = [label.asset_id for label in labels]
        if any(asset_id is None for asset_id in asset_id_array):
            external_id_array = [label.asset_external_id for label in labels]
            asset_id_array = AssetUseCasesUtils(
                self._kili_api_gateway
            ).get_asset_ids_or_throw_error(
                asset_ids=None,
                external_ids=external_id_array,  # pyright: ignore[reportGeneralTypeIssues]
                project_id=project_id,
            )

        labels_to_add = [
            AppendLabelData(
                author_id=label.author_id,
                asset_id=asset_id,  # pyright: ignore[reportGeneralTypeIssues]
                seconds_to_label=label.seconds_to_label,
                json_response=label.json_response,
                model_name=label.model_name,
                client_version=None,
            )
            for label, asset_id in zip(labels, asset_id_array)
        ]

        data = AppendManyLabelsData(
            label_type=label_type,
            overwrite=overwrite,
            labels_data=labels_to_add,
        )
        return self._kili_api_gateway.append_many_labels(
            fields=fields,
            disable_tqdm=disable_tqdm,
            data=data,
            project_id=project_id,
        )

    def append_to_labels(
        self,
        author_id: Optional[UserId],
        json_response: Dict,
        label_type: LabelType,
        seconds_to_label: Optional[float],
        asset_id: AssetId,
        fields: ListOrTuple[str],
    ) -> Dict:
        """Append to labels."""
        data = AppendToLabelsData(
            author_id=(
                author_id
                if author_id is not None
                else self._kili_api_gateway.get_current_user(fields=("id",))["id"]
            ),
            json_response=json_response,
            label_type=label_type,
            seconds_to_label=seconds_to_label,
            client_version=None,
            skipped=None,
        )
        return self._kili_api_gateway.append_to_labels(data=data, asset_id=asset_id, fields=fields)

    def create_honeypot_label(
        self,
        json_response: Dict,
        asset_id: Optional[AssetId],
        asset_external_id: Optional[AssetExternalId],
        project_id: Optional[ProjectId],
        fields: ListOrTuple[str],
    ) -> Dict:
        """Create honeypot label."""
        if asset_id is None:
            if asset_external_id is None or project_id is None:
                raise ValueError(
                    "Either provide `asset_id` or `asset_external_id` and `project_id`."
                )

            asset_id = AssetUseCasesUtils(self._kili_api_gateway).infer_ids_from_external_ids(
                asset_external_ids=[asset_external_id],
                project_id=project_id,
            )[asset_external_id]

        return self._kili_api_gateway.create_honeypot_label(
            json_response=json_response, asset_id=asset_id, fields=fields
        )

    def export_labels_as_df(
        self,
        *,
        project_id: ProjectId,
        label_fields: ListOrTuple[str],
        asset_fields: ListOrTuple[str],
    ) -> "pd.DataFrame":
        """Export labels as a pandas DataFrame."""
        assets_gen = self._kili_api_gateway.list_assets(
            AssetFilters(project_id=ProjectId(project_id)),
            tuple(asset_fields) + tuple("labels." + field for field in label_fields),
            QueryOptions(disable_tqdm=False),
        )

        labels = [
            dict(
                label,
                **{f"asset_{key}": asset[key] for key in asset if key != "labels"},
            )
            for asset in assets_gen
            for label in asset["labels"]
        ]

        import pandas as pd  # pylint: disable=import-outside-toplevel

        return pd.DataFrame(labels)
