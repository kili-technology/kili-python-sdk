"""CLI's project export subcommand"""

from typing import Optional, cast

import click
from typeguard import typechecked
from typing_extensions import get_args

from kili import services
from kili.cli.common_args import Options
from kili.cli.helpers import get_kili_client
from kili.services.export.exceptions import NoCompatibleJobError
from kili.services.export.types import LabelFormat, SplitOption
from kili.services.types import ProjectId


@click.command(name="export")
@click.option(
    "--output-format",
    type=click.Choice(get_args(LabelFormat)),
    help="Format into which the label data will be converted",
    required=True,
)
@click.option(
    "--output-file", type=str, help="File into which the labels are saved.", required=True
)
@click.option(
    "--layout",
    type=click.Choice(get_args(SplitOption)),
    default="merged",
    help="Layout of the label files",
)
@click.option(
    "--single-file",
    type=bool,
    is_flag=True,
    help="Layout of the label files",
)
@Options.api_key
@Options.endpoint
@Options.project_id
@Options.verbose
@typechecked
# pylint: disable=too-many-arguments
def export_labels(
    output_format: LabelFormat,
    output_file: str,
    layout: SplitOption,
    single_file: bool,
    api_key: Optional[str],
    endpoint: Optional[str],
    project_id: str,
    verbose: bool,  # pylint: disable=unused-argument
):
    """
    Export the Kili labels of a project to a given format.

    \b
    The supported formats are:
    - Yolo V4, V5, V7 for object detection (bounding box) tasks.
    - Kili for all tasks.
    - COCO (coming soon) for object detection tasks.
    - Pascal VOC (coming soon) for object detection tasks.
    \b
    \b
    !!! Examples
        ```
        kili project export \\
            --project-id <project_id> \\
            --output-format yolo_v5 \\
            --output-file /tmp/export.zip
        ```
        ```
        kili project export \\
            --project-id <project_id> \\
            --output-format yolo_v4 \\
            --output-file /tmp/export_split.zip \\
            --layout split
        ```
    \b
    \b
    !!! warning "Unsupported exports"
        Currently, this command does not support the export of videos that have not
        been cut into separated frames.

        For such exports, please use the Kili UI.
    """
    kili = get_kili_client(api_key=api_key, api_endpoint=endpoint)

    try:
        services.export_labels(
            kili,
            asset_ids=None,
            project_id=cast(ProjectId, project_id),
            export_type="latest",
            label_format=output_format,
            split_option=layout,
            single_file=single_file,
            output_file=output_file,
            disable_tqdm=not verbose,
            log_level="INFO" if verbose else "WARNING",
        )
    except NoCompatibleJobError as excp:
        print(str(excp))
