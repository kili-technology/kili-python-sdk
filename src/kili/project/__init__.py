"""Project module."""
from typing import List, Optional, cast

from typeguard import typechecked

from kili import services
from kili.services.export.types import LabelFormat, SplitOption
from kili.services.types import AssetId, InputType, LabelType, LogLevel, ProjectId


class Project:  # pylint: disable=too-few-public-methods
    """
    Object that represents a project in Kili.
    It allows management operations such as uploading assets, uploading predictions,
    modifying the project's queue etc.
    It also allows queries from this project such as its assets, labels etc.
    """

    def __init__(  # pylint: disable=too-many-arguments
        self, project_id: ProjectId, input_type: InputType, title: str, client
    ):
        self.project_id = project_id
        self.title = title
        self.input_type = input_type
        self.client = client

    @typechecked
    def export(  # pylint: disable=too-many-arguments
        self,
        filename: str,
        fmt: LabelFormat,
        asset_ids: Optional[List[AssetId]] = None,
        layout: SplitOption = "split",
        single_file: bool = False,
        disable_tqdm: bool = False,
        log_level: LogLevel = "INFO",
        with_assets: bool = True,
    ) -> None:
        """Export the project assets with the requested format into the requested output path.

        Usage:
        ```
        from kili.client import Kili
        kili = Kili()
        project = kili.get_project("your_project_id")
        project.export("export.zip", fmt="yolo_v4")
        ```

        Args:
            filename: Relative or full path of the archive that will contain
                the exported data.
            fmt: Format of the exported labels.
            asset_ids: Optional list of the assets from which to export the labels.
            layout: Layout of the exported files: "split" means there is one folder
                per job, "merged" that there is one folder with every labels.
            single_file: Layout of the exported labels. Single file mode is
                only available for some specific formats (COCO and Kili).
            disable_tqdm: Disable the progress bar if True.
            log_level: Level of debugging.
            with_assets: Download the assets in the export.
        """
        services.export_labels(
            self.client,
            asset_ids=cast(Optional[List[str]], asset_ids),
            project_id=self.project_id,
            export_type="latest",
            label_format=fmt,
            split_option=layout,
            single_file=single_file,
            output_file=filename,
            disable_tqdm=disable_tqdm,
            log_level=log_level,
            with_assets=with_assets,
        )

    @typechecked
    def append_labels(
        self,
        labels: List[dict],
        label_type: LabelType = "DEFAULT",
        model_name: Optional[str] = None,
    ):
        """Append labels to assets.

        !!! info "fields of labels to append"
            Either provide an asset_id or an external_id
            ```
            class LabelData:
                asset_id: str
                asset_external_id: str
                json_response: Required[Dict]
                author_id: str
                seconds_to_label: int
            ```

        Args:
            labels: list of dictionnaries with informations about the labels to create.
            label_type: Can be one of `AUTOSAVE`, `DEFAULT`, `PREDICTION`, `REVIEW` or `INFERENCE`

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.

        Examples:
            >>> kili.append_to_labels(
                    [
                        {'json_response': {...}, asset_id: 'cl9wmlkuc00050qsz6ut39g8h'},
                        {'json_response': {...}, asset_id: 'cl9wmlkuw00080qsz2kqh8aiy'}
                    ]
                )

        """
        return services.import_labels_from_dict(
            self.client, self.project_id, labels, label_type, model_name
        )
