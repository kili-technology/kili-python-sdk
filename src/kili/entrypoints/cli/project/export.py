"""CLI's project export subcommand."""

from typing import Optional, cast

import click
from typeguard import typechecked
from typing_extensions import get_args

from kili.domain.project import ProjectId
from kili.entrypoints.cli.common_args import Options
from kili.entrypoints.cli.helpers import get_kili_client
from kili.services.export import export_labels as service_export_labels
from kili.services.export.exceptions import NoCompatibleJobError
from kili.services.export.types import LabelFormat, SplitOption


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
    help=(
        "Layout of the label files: 'split' to group labels per job, 'merged' to have one folder"
        " with every labels."
    ),
)
@click.option(
    "--single-file",
    type=bool,
    is_flag=True,
    help=(
        "Layout of the label files. Single file mode is only available for some specific formats"
        " (COCO and Kili)."
    ),
)
@click.option(
    "--with-assets/--without-assets",
    type=bool,
    default=True,
    help="Download assets in the export.",
)
@click.option(
    "--normalized-coordinates/--pixel-coordinates",
    type=bool,
    default=None,
    help="Whether to use normalized coordinates or not.",
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
    verbose: bool,
    with_assets: bool,
    normalized_coordinates: Optional[bool],
) -> None:
    # pylint: disable=line-too-long
    """Export the Kili labels of a project to a given format.

    \b
    !!! Info
        The supported formats are:

        - Yolo V4, V5, V7, V8 for object detection tasks.
        - Kili (a.k.a raw) for all tasks.
        - COCO for object detection tasks (bounding box and semantic segmentation).
        - Pascal VOC for object detection tasks (bounding box).
    \b
    \b
    !!! warning "Cloud storage"
        Export with asset download (`--with-assets`) is not allowed for projects connected to a cloud storage.
    \b
    \b
    !!! Examples
        ```
        kili project export \\
            --project-id <project_id> \\
            --output-format coco \\
            --output-file /tmp/export.zip
        ```
        ```
        kili project export \\
            --project-id <project_id> \\
            --output-format yolo_v5 \\
            --output-file /tmp/export_split.zip \\
            --layout split
        ```
    """
    kili = get_kili_client(api_key=api_key, api_endpoint=endpoint)

    try:
        service_export_labels(
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
            with_assets=with_assets,
            annotation_modifier=None,
            asset_filter_kwargs=None,
            normalized_coordinates=normalized_coordinates,
        )
    except NoCompatibleJobError as excp:
        print(str(excp))
