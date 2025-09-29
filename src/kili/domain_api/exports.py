"""Tags domain namespace for the Kili Python SDK."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, TypedDict, Union

from typeguard import typechecked
from typing_extensions import deprecated

from kili.domain.asset.asset import AssetStatus, StatusInStep
from kili.domain.issue import IssueStatus, IssueType
from kili.domain.label import LabelType
from kili.domain.types import ListOrTuple
from kili.domain_api.base import DomainNamespace
from kili.domain_api.namespace_utils import get_available_methods
from kili.services.export.types import CocoAnnotationModifier, LabelFormat, SplitOption

if TYPE_CHECKING:
    import pandas as pd


class ExportAssetFilter(TypedDict, total=False):
    """Filter options for asset export operations.

    All fields are optional and can be combined to filter assets during export.
    """

    assignee_in: Optional[ListOrTuple[str]]
    assignee_not_in: Optional[ListOrTuple[str]]
    consensus_mark_gte: Optional[float]
    consensus_mark_lte: Optional[float]
    created_at_gte: Optional[str]
    created_at_lte: Optional[str]
    external_id_in: Optional[List[str]]
    external_id_strictly_in: Optional[List[str]]
    honeypot_mark_gte: Optional[float]
    honeypot_mark_lte: Optional[float]
    inference_mark_gte: Optional[float]
    inference_mark_lte: Optional[float]
    issue_status: Optional[IssueStatus]
    issue_type: Optional[IssueType]
    label_author_in: Optional[List[str]]
    label_category_search: Optional[str]
    label_labeler_in: Optional[ListOrTuple[str]]
    label_labeler_not_in: Optional[ListOrTuple[str]]
    label_reviewer_in: Optional[ListOrTuple[str]]
    label_reviewer_not_in: Optional[ListOrTuple[str]]
    metadata_where: Optional[Dict[str, Any]]
    skipped: Optional[bool]
    status_in: Optional[List[AssetStatus]]
    step_name_in: Optional[List[str]]
    step_status_in: Optional[List[StatusInStep]]


class ExportNamespace(DomainNamespace):
    """Export domain namespace providing export-related operations."""

    def __init__(self, client, gateway):
        """Initialize the exports namespace.

        Args:
            client: The Kili client instance
            gateway: The KiliAPIGateway instance for API operations
        """
        super().__init__(client, gateway, "exports")
        self.raw = self.kili

    @deprecated(
        "'exports' is a namespace, not a callable method. "
        "Use kili.exports.kili() or other available methods instead."
    )
    def __call__(self, *args, **kwargs):
        """Raise a helpful error when namespace is called like a method.

        This provides guidance to users migrating from the legacy API
        where exports were accessed via kili.exports(...) to the new domain API
        where they use kili.exports.kili(...) or other format-specific methods.
        """
        available_methods = get_available_methods(self)
        methods_str = ", ".join(f"kili.{self._domain_name}.{m}()" for m in available_methods)
        raise TypeError(
            f"'{self._domain_name}' is a namespace, not a callable method. "
            f"The legacy API has been replaced with the domain API.\n"
            f"Available export formats: {methods_str}\n"
            f"Example: kili.{self._domain_name}.kili(...) or kili.{self._domain_name}.coco(...)"
        )

    def kili(
        self,
        project_id: str,
        output_path: str,
        with_assets: Optional[bool] = False,
        disable_tqdm: Optional[bool] = False,
        filter: Optional[ExportAssetFilter] = None,
        include_sent_back_labels: Optional[bool] = None,
        label_type_in: Optional[List[LabelType]] = None,
        single_file: Optional[bool] = False,
    ):
        """Export project labels in Kili native format.

        Kili native format exports annotations as JSON files containing the raw label data
        with all metadata and annotation details preserved.

        Args:
            project_id: Identifier of the project.
            output_path: Relative or full path of the archive that will contain
                the exported data.
            with_assets: Download the assets in the export.
            disable_tqdm: Disable the progress bar if True.
            filter: Optional dictionary to filter assets whose labels are exported.
                See `ExportAssetFilter` for available filter options.
            include_sent_back_labels: If True, the export will include the labels that
                have been sent back.
            label_type_in: Optional list of label type. Exported assets should have a label
                whose type belongs to that list.
                By default, only `DEFAULT` and `REVIEW` labels are exported.
            single_file: If True, all labels are exported in a single JSON file.

        Returns:
            Export information or None if export failed.
        """
        return self._export(
            project_id=project_id,
            output_path=output_path,
            with_assets=with_assets,
            disable_tqdm=disable_tqdm,
            filter=filter,
            include_sent_back_labels=include_sent_back_labels,
            label_type_in=label_type_in,
            normalized_coordinates=True,
            fmt="kili",
            single_file=bool(single_file),
        )

    def coco(
        self,
        project_id: str,
        output_path: str,
        annotation_modifier: Optional[CocoAnnotationModifier] = None,
        with_assets: Optional[bool] = True,
        disable_tqdm: Optional[bool] = False,
        filter: Optional[ExportAssetFilter] = None,
        include_sent_back_labels: Optional[bool] = None,
        label_type_in: Optional[List[LabelType]] = None,
        layout: SplitOption = "split",
    ):
        """Export project labels in COCO format.

        COCO format exports annotations in JSON format with image metadata and
        category information, suitable for object detection and segmentation tasks.

        Args:
            project_id: Identifier of the project.
            output_path: Relative or full path of the archive that will contain
                the exported data.
            annotation_modifier: Function that takes the COCO annotation, the
                COCO image, and the Kili annotation, and returns an updated COCO annotation.
            with_assets: Download the assets in the export.
            disable_tqdm: Disable the progress bar if True.
            filter: Optional dictionary to filter assets whose labels are exported.
                See `ExportAssetFilter` for available filter options.
            include_sent_back_labels: If True, the export will include the labels that
                have been sent back.
            label_type_in: Optional list of label type. Exported assets should have a label
                whose type belongs to that list.
                By default, only `DEFAULT` and `REVIEW` labels are exported.
            layout: Layout of the exported files. "split" means there is one folder
                per job, "merged" that there is one folder with every labels.

        Returns:
            Export information or None if export failed.
        """
        return self._export(
            project_id=project_id,
            annotation_modifier=annotation_modifier,
            output_path=output_path,
            with_assets=with_assets,
            disable_tqdm=disable_tqdm,
            filter=filter,
            include_sent_back_labels=include_sent_back_labels,
            label_type_in=label_type_in,
            layout=layout,
            fmt="coco",
        )

    def yolo_v4(
        self,
        project_id: str,
        output_path: str,
        layout: SplitOption = "split",
        with_assets: Optional[bool] = True,
        disable_tqdm: Optional[bool] = False,
        filter: Optional[ExportAssetFilter] = None,
        include_sent_back_labels: Optional[bool] = None,
        label_type_in: Optional[List[LabelType]] = None,
    ):
        """Export project labels in YOLO v4 format.

        YOLO v4 format exports annotations with normalized coordinates suitable for
        object detection tasks. The format creates a classes.txt file and individual
        .txt files for each image with bounding box annotations.

        Args:
            project_id: Identifier of the project.
            output_path: Relative or full path of the archive that will contain
                the exported data.
            layout: Layout of the exported files. "split" means there is one folder
                per job, "merged" that there is one folder with every labels.
            with_assets: Download the assets in the export.
            disable_tqdm: Disable the progress bar if True.
            filter: Optional dictionary to filter assets whose labels are exported.
                See `ExportAssetFilter` for available filter options.
            label_type_in: Optional list of label type. Exported assets should have a label
                whose type belongs to that list.
                By default, only `DEFAULT` and `REVIEW` labels are exported.
            include_sent_back_labels: If True, the export will include the labels that
                have been sent back.

        Returns:
            Export information or None if export failed.
        """
        return self._export(
            project_id=project_id,
            output_path=output_path,
            with_assets=with_assets,
            disable_tqdm=disable_tqdm,
            filter=filter,
            include_sent_back_labels=include_sent_back_labels,
            label_type_in=label_type_in,
            layout=layout,
            fmt="yolo_v4",
        )

    def yolo_v5(
        self,
        project_id: str,
        output_path: str,
        layout: SplitOption = "split",
        with_assets: Optional[bool] = True,
        disable_tqdm: Optional[bool] = False,
        filter: Optional[ExportAssetFilter] = None,
        include_sent_back_labels: Optional[bool] = None,
        label_type_in: Optional[List[LabelType]] = None,
    ):
        """Export project labels in YOLO v5 format.

        YOLO v5 format exports annotations with normalized coordinates suitable for
        object detection tasks. The format creates a data.yaml file and individual
        .txt files for each image with bounding box annotations.

        Args:
            project_id: Identifier of the project.
            output_path: Relative or full path of the archive that will contain
                the exported data.
            layout: Layout of the exported files. "split" means there is one folder
                per job, "merged" that there is one folder with every labels.
            with_assets: Download the assets in the export.
            disable_tqdm: Disable the progress bar if True.
            filter: Optional dictionary to filter assets whose labels are exported.
                See `ExportAssetFilter` for available filter options.
            label_type_in: Optional list of label type. Exported assets should have a label
                whose type belongs to that list.
                By default, only `DEFAULT` and `REVIEW` labels are exported.
            include_sent_back_labels: If True, the export will include the labels that
                have been sent back.

        Returns:
            Export information or None if export failed.
        """
        return self._export(
            project_id=project_id,
            output_path=output_path,
            with_assets=with_assets,
            disable_tqdm=disable_tqdm,
            filter=filter,
            include_sent_back_labels=include_sent_back_labels,
            label_type_in=label_type_in,
            layout=layout,
            fmt="yolo_v5",
        )

    def yolo_v7(
        self,
        project_id: str,
        output_path: str,
        layout: SplitOption = "split",
        with_assets: Optional[bool] = True,
        disable_tqdm: Optional[bool] = False,
        filter: Optional[ExportAssetFilter] = None,
        include_sent_back_labels: Optional[bool] = None,
        label_type_in: Optional[List[LabelType]] = None,
    ):
        """Export project labels in YOLO v7 format.

        YOLO v7 format exports annotations with normalized coordinates suitable for
        object detection tasks. The format creates a data.yaml file and individual
        .txt files for each image with bounding box annotations.

        Args:
            project_id: Identifier of the project.
            output_path: Relative or full path of the archive that will contain
                the exported data.
            layout: Layout of the exported files. "split" means there is one folder
                per job, "merged" that there is one folder with every labels.
            with_assets: Download the assets in the export.
            disable_tqdm: Disable the progress bar if True.
            filter: Optional dictionary to filter assets whose labels are exported.
                See `ExportAssetFilter` for available filter options.
            label_type_in: Optional list of label type. Exported assets should have a label
                whose type belongs to that list.
                By default, only `DEFAULT` and `REVIEW` labels are exported.
            include_sent_back_labels: If True, the export will include the labels that
                have been sent back.

        Returns:
            Export information or None if export failed.
        """
        return self._export(
            project_id=project_id,
            output_path=output_path,
            with_assets=with_assets,
            disable_tqdm=disable_tqdm,
            filter=filter,
            include_sent_back_labels=include_sent_back_labels,
            label_type_in=label_type_in,
            layout=layout,
            fmt="yolo_v7",
        )

    def yolo_v8(
        self,
        project_id: str,
        output_path: str,
        layout: SplitOption = "split",
        with_assets: Optional[bool] = True,
        disable_tqdm: Optional[bool] = False,
        filter: Optional[ExportAssetFilter] = None,
        include_sent_back_labels: Optional[bool] = None,
        label_type_in: Optional[List[LabelType]] = None,
    ):
        """Export project labels in YOLO v8 format.

        YOLO v8 format exports annotations with normalized coordinates suitable for
        object detection tasks. The format creates a data.yaml file and individual
        .txt files for each image with bounding box annotations.

        Args:
            project_id: Identifier of the project.
            output_path: Relative or full path of the archive that will contain
                the exported data.
            layout: Layout of the exported files. "split" means there is one folder
                per job, "merged" that there is one folder with every labels.
            with_assets: Download the assets in the export.
            disable_tqdm: Disable the progress bar if True.
            filter: Optional dictionary to filter assets whose labels are exported.
                See `ExportAssetFilter` for available filter options.
            label_type_in: Optional list of label type. Exported assets should have a label
                whose type belongs to that list.
                By default, only `DEFAULT` and `REVIEW` labels are exported.
            include_sent_back_labels: If True, the export will include the labels that
                have been sent back.

        Returns:
            Export information or None if export failed.
        """
        return self._export(
            project_id=project_id,
            output_path=output_path,
            with_assets=with_assets,
            disable_tqdm=disable_tqdm,
            filter=filter,
            include_sent_back_labels=include_sent_back_labels,
            label_type_in=label_type_in,
            layout=layout,
            fmt="yolo_v8",
        )

    def pascal_voc(
        self,
        project_id: str,
        output_path: str,
        with_assets: Optional[bool] = True,
        disable_tqdm: Optional[bool] = False,
        filter: Optional[ExportAssetFilter] = None,
        include_sent_back_labels: Optional[bool] = None,
        label_type_in: Optional[List[LabelType]] = None,
    ):
        """Export project labels in Pascal VOC format.

        Pascal VOC format exports annotations in XML format with pixel coordinates,
        suitable for object detection tasks. Each image has a corresponding XML file
        with bounding box annotations in the Pascal VOC XML schema.

        Args:
            project_id: Identifier of the project.
            output_path: Relative or full path of the archive that will contain
                the exported data.
            with_assets: Download the assets in the export.
            disable_tqdm: Disable the progress bar if True.
            filter: Optional dictionary to filter assets whose labels are exported.
                See `ExportAssetFilter` for available filter options.
            label_type_in: Optional list of label type. Exported assets should have a label
                whose type belongs to that list.
                By default, only `DEFAULT` and `REVIEW` labels are exported.
            include_sent_back_labels: If True, the export will include the labels that
                have been sent back.

        Returns:
            Export information or None if export failed.
        """
        return self._export(
            project_id=project_id,
            output_path=output_path,
            with_assets=with_assets,
            disable_tqdm=disable_tqdm,
            filter=filter,
            include_sent_back_labels=include_sent_back_labels,
            label_type_in=label_type_in,
            layout="merged",
            fmt="pascal_voc",
        )

    def geojson(
        self,
        project_id: str,
        output_path: str,
        with_assets: Optional[bool] = True,
        disable_tqdm: Optional[bool] = False,
        filter: Optional[ExportAssetFilter] = None,
        include_sent_back_labels: Optional[bool] = None,
        label_type_in: Optional[List[LabelType]] = None,
    ):
        """Export project labels in GeoJSON format.

        GeoJSON format exports annotations with latitude/longitude coordinates,
        suitable for geospatial object detection tasks. This format is compatible
        with IMAGE and GEOSPATIAL project types.

        Args:
            project_id: Identifier of the project.
            output_path: Relative or full path of the archive that will contain
                the exported data.
            with_assets: Download the assets in the export.
            disable_tqdm: Disable the progress bar if True.
            filter: Optional dictionary to filter assets whose labels are exported.
                See `ExportAssetFilter` for available filter options.
            label_type_in: Optional list of label type. Exported assets should have a label
                whose type belongs to that list.
                By default, only `DEFAULT` and `REVIEW` labels are exported.
            include_sent_back_labels: If True, the export will include the labels that
                have been sent back.

        Returns:
            Export information or None if export failed.
        """
        return self._export(
            project_id=project_id,
            output_path=output_path,
            with_assets=with_assets,
            disable_tqdm=disable_tqdm,
            filter=filter,
            include_sent_back_labels=include_sent_back_labels,
            label_type_in=label_type_in,
            layout="merged",
            fmt="geojson",
        )

    @typechecked
    def dataframe(
        self,
        project_id: str,
        label_fields: ListOrTuple[str] = (
            "author.email",
            "author.id",
            "createdAt",
            "id",
            "labelType",
        ),
        asset_fields: ListOrTuple[str] = ("externalId",),
    ) -> "pd.DataFrame":
        """Export project labels as a pandas DataFrame.

        This method returns label metadata in a structured pandas DataFrame format,
        making it easy to analyze and manipulate label data using pandas operations.
        Unlike file-based export methods, this returns the data directly in memory.

        Args:
            project_id: Identifier of the project.
            label_fields: All the fields to request among the possible fields for the labels.
                See [the documentation](https://api-docs.kili-technology.com/types/objects/label)
                for all possible fields.
            asset_fields: All the fields to request among the possible fields for the assets.
                See [the documentation](https://api-docs.kili-technology.com/types/objects/asset)
                for all possible fields.

        Returns:
            A pandas DataFrame containing the labels with the requested fields.

        Examples:
            >>> # Export labels with default fields
            >>> df = kili.exports.dataframe(project_id="project_id")

            >>> # Export labels with custom fields
            >>> df = kili.exports.dataframe(
            ...     project_id="project_id",
            ...     label_fields=["author.email", "id", "labelType", "createdAt", "jsonResponse"],
            ...     asset_fields=["externalId", "id", "content"]
            ... )

            >>> # Analyze label data with pandas
            >>> df.groupby("labelType").size()
            >>> df[df["author.email"] == "user@example.com"]
        """
        return self._client.export_labels_as_df(
            project_id=project_id,
            fields=label_fields,
            asset_fields=asset_fields,
        )

    def _export(
        self,
        *,
        annotation_modifier: Optional[CocoAnnotationModifier] = None,
        disable_tqdm: Optional[bool] = None,
        output_path: str,
        filter: Optional[ExportAssetFilter] = None,
        fmt: LabelFormat,
        include_sent_back_labels: Optional[bool] = None,
        label_type_in: Optional[List[LabelType]],
        layout: SplitOption = "split",
        normalized_coordinates: Optional[bool] = None,
        project_id: str,
        single_file: bool = False,
        with_assets: Optional[bool] = True,
    ) -> Optional[List[Dict[str, Union[List[str], str]]]]:
        """Export the project labels with the requested format into the requested output path.

        Args:
            project_id: Identifier of the project.
            output_path: Relative or full path of the archive that will contain
                the exported data.
            fmt: Format of the exported labels.
            layout: Layout of the exported files. "split" means there is one folder
                per job, "merged" that there is one folder with every labels.
            single_file: Layout of the exported labels. Single file mode is
                only available for some specific formats (COCO and Kili).
            disable_tqdm: Disable the progress bar if True.
            with_assets: Download the assets in the export.
            annotation_modifier: (For COCO export only) function that takes the COCO annotation, the
                COCO image, and the Kili annotation, and should return an updated COCO annotation.
            filter: Optional dictionary to filter assets whose labels are exported.
                See `ExportAssetFilter` for available filter options.
            normalized_coordinates: This parameter is only effective on the Kili (a.k.a raw) format.
                If True, the coordinates of the `(x, y)` vertices are normalized between 0 and 1.
                If False, the json response will contain additional fields with coordinates in
                absolute values, that is, in pixels.
            label_type_in: Optional list of label type. Exported assets should have a label
                whose type belongs to that list.
                By default, only `DEFAULT` and `REVIEW` labels are exported.
            include_sent_back_labels: If True, the export will include the labels that have been sent back.

        Returns:
            Export information or None if export failed.

        Examples:
            >>> # Export all labels in COCO format
            >>> kili.labels.export(
            ...     project_id="my_project",
            ...     fmt="coco",
            ...     filename="export.zip"
            ... )

            >>> # Export labels for specific assets
            >>> kili.labels.export(
            ...     project_id="my_project",
            ...     fmt="kili",
            ...     filename="filtered_export.zip",
            ...     filter={"external_id_contains": ["batch_1"]}
            ... )
        """
        asset_filter_kwargs = dict(filter) if filter else {}
        return self._client.export_labels(
            project_id=project_id,
            filename=output_path,
            fmt=fmt,
            layout=layout,
            single_file=single_file,
            disable_tqdm=disable_tqdm,
            with_assets=bool(with_assets),
            annotation_modifier=annotation_modifier,
            asset_filter_kwargs=asset_filter_kwargs,
            normalized_coordinates=normalized_coordinates,
            label_type_in=list(label_type_in) if label_type_in else None,
            include_sent_back_labels=include_sent_back_labels,
        )
