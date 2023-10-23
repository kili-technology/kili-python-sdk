"""Label queries."""

from typing import TYPE_CHECKING, Dict, List, Optional, cast

from typeguard import typechecked

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.domain.asset import AssetExternalId, AssetFilters
from kili.domain.asset.asset import AssetId
from kili.domain.project import ProjectId
from kili.domain.types import ListOrTuple
from kili.entrypoints.base import BaseOperationEntrypointMixin
from kili.services.export import export_labels
from kili.services.export.exceptions import NoCompatibleJobError
from kili.services.export.types import CocoAnnotationModifier, LabelFormat, SplitOption
from kili.services.project import get_project
from kili.use_cases.asset.utils import AssetUseCasesUtils
from kili.utils.logcontext import for_all_methods, log_call

if TYPE_CHECKING:
    import pandas as pd


@for_all_methods(log_call, exclude=["__init__"])
class QueriesLabel(BaseOperationEntrypointMixin):
    """Set of Label queries."""

    # pylint: disable=too-many-arguments,too-many-locals

    @typechecked
    def export_labels_as_df(
        self,
        project_id: str,
        fields: ListOrTuple[str] = ("author.email", "author.id", "createdAt", "id", "labelType"),
        asset_fields: ListOrTuple[str] = ("externalId",),
    ) -> "pd.DataFrame":
        # pylint: disable=line-too-long
        """Get the labels of a project as a pandas DataFrame.

        Args:
            project_id: Identifier of the project
            fields: All the fields to request among the possible fields for the labels.
                See [the documentation](https://docs.kili-technology.com/reference/graphql-api#label) for all possible fields.
            asset_fields: All the fields to request among the possible fields for the assets.
                See [the documentation](https://docs.kili-technology.com/reference/graphql-api#asset) for all possible fields.

        Returns:
            A pandas DataFrame containing the labels.
        """
        get_project(self, project_id, ["id"])
        assets_gen = self.kili_api_gateway.list_assets(
            AssetFilters(project_id=ProjectId(project_id)),
            tuple(asset_fields) + tuple("labels." + field for field in fields),
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

    def export_labels(
        self,
        project_id: str,
        filename: str,
        fmt: LabelFormat,
        asset_ids: Optional[List[str]] = None,
        layout: SplitOption = "split",
        single_file: bool = False,
        disable_tqdm: Optional[bool] = None,
        with_assets: bool = True,
        external_ids: Optional[List[str]] = None,
        annotation_modifier: Optional[CocoAnnotationModifier] = None,
        asset_filter_kwargs: Optional[Dict[str, object]] = None,
        normalized_coordinates: Optional[bool] = None,
    ) -> None:
        # pylint: disable=line-too-long
        """Export the project labels with the requested format into the requested output path.

        Args:
            project_id: Identifier of the project.
            filename: Relative or full path of the archive that will contain
                the exported data.
            fmt: Format of the exported labels.
            asset_ids: Optional list of the assets internal IDs from which to export the labels.
            layout: Layout of the exported files. "split" means there is one folder
                per job, "merged" that there is one folder with every labels.
            single_file: Layout of the exported labels. Single file mode is
                only available for some specific formats (COCO and Kili).
            disable_tqdm: Disable the progress bar if True.
            with_assets: Download the assets in the export.
            external_ids: Optional list of the assets external IDs from which to export the labels.
            annotation_modifier: (For COCO export only) function that takes the COCO annotation, the
                COCO image, and the Kili annotation, and should return an updated COCO annotation.
                This can be used if you want to add a new attribute to the COCO annotation. For
                example, you can add a method that computes if the annotation is a rectangle or not
                and add it to the COCO annotation (see example).
            asset_filter_kwargs: Optional dictionary of arguments to pass to `kili.assets()` in order to filter the assets the labels are exported from. The supported arguments are:

                - `consensus_mark_gte`
                - `consensus_mark_lte`
                - `external_id_strictly_in`
                - `external_id_in`
                - `honeypot_mark_gte`
                - `honeypot_mark_lte`
                - `label_author_in`
                - `label_reviewer_in`
                - `skipped`
                - `status_in`
                - `label_category_search`
                - `created_at_gte`
                - `created_at_lte`
                - `issue_type`
                - `issue_status`
                - `inference_mark_gte`
                - `inference_mark_lte`
                - `metadata_where`

                See the documentation of [`kili.assets()`](https://python-sdk-docs.kili-technology.com/latest/sdk/asset/#kili.queries.asset.__init__.QueriesAsset.assets) for more information.
            normalized_coordinates: This parameter is only effective on the Kili (a.k.a raw) format.
                If True, the coordinates of the `(x, y)` vertices are normalized between 0 and 1.
                If False, the json response will contain additional fields with coordinates in absolute values, that is, in pixels.

        !!! Info
            The supported formats are:

            - Yolo V4, V5, V7, V8 for object detection tasks.
            - Kili (a.k.a raw) for all tasks.
            - COCO for object detection tasks (bounding box and semantic segmentation).
            - Pascal VOC for object detection tasks (bounding box).

        !!! warning "Cloud storage"
            Export with asset download (`with_assets=True`) is not allowed for projects connected to a cloud storage.

        !!! Example
            ```python
            kili.export_labels("your_project_id", "export.zip", "yolo_v4")
            ```

        !!! Example
            ```python
            def is_rectangle(coco_annotation, coco_image, kili_annotation):
                is_rectangle = ...
                return {**coco_annotation, "attributes": {"is_rectangle": is_rectangle}}

            kili.export_labels(
                "your_project_id",
                "export.zip",
                "coco",
                annotation_modifier=add_is_rectangle
            )
            ```
        """
        if external_ids is not None and asset_ids is None:
            id_map = AssetUseCasesUtils(self.kili_api_gateway).infer_ids_from_external_ids(
                asset_external_ids=cast(List[AssetExternalId], external_ids),
                project_id=ProjectId(project_id),
            )
            resolved_asset_ids = [id_map[AssetExternalId(i)] for i in external_ids]
        else:
            resolved_asset_ids = cast(List[AssetId], asset_ids)

        try:
            export_labels(
                self,
                asset_ids=resolved_asset_ids,
                project_id=ProjectId(project_id),
                export_type="latest",
                label_format=fmt,
                split_option=layout,
                single_file=single_file,
                output_file=filename,
                disable_tqdm=disable_tqdm,
                log_level="WARNING",
                with_assets=with_assets,
                annotation_modifier=annotation_modifier,
                asset_filter_kwargs=asset_filter_kwargs,
                normalized_coordinates=normalized_coordinates,
            )
        except NoCompatibleJobError as excp:
            print(str(excp))
