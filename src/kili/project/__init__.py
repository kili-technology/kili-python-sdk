"""Project module."""
from typing import List, Optional, cast

from typeguard import typechecked

from kili import services
from kili.services.export.types import LabelFormat, SplitOption
from kili.services.types import AssetId, InputType, LogLevel, ProjectId


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
    ) -> None:
        """Export the project assets with the requested format into the requested output path.

        Usage:
        ```
        from kili.client import Kili
        kili = Kili()
        project = kili.get_project("your_project_id")
        project.export("export.zip", output_format="yolo_v4")
        ```

        Args:
            filename: Relative or full path of the archive that will contain
                the exported data.
            output_format: Format of the exported labels.
            asset_ids: Optional list of the assets from which to export the labels.
            layout: Layout of the exported files: "split" means there is one folder
                per job, "merged" that there is one folder with every labels.
            disable_tqdm: Disable the progress bar if True.
            log_level: Level of debugging.
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
        )
