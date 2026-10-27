"""CLI's project export subcommand."""

from typing import Optional, cast, get_args

import click
from typeguard import typechecked

from kili.domain.project import ProjectId
from kili.entrypoints.cli.common_args import Options
from kili.entrypoints.cli.helpers import get_kili_client
from kili.services.export import export_labels as service_export_labels
from kili.services.export.exceptions import NoCompatibleJobError, NotCompatibleOptions
from kili.services.export.types import LabelFormat, SplitOption, YoloBoundingBoxes


@click.command(name="export")
@click.option(
    "--output-format",
    type=click.Choice(get_args(LabelFormat)),
    help=(
        "Format into which the label data will be converted. yolo_v4, yolo_v5, yolo_v7 and"
        " yolo_v8 are deprecated: use yolo."
    ),
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
@click.option(
    "--bbox-as",
    type=click.Choice(get_args(YoloBoundingBoxes)),
    default="box",
    help=(
        "YOLO only: write the bounding boxes for the Detect task ('box'), the OBB task ('obb'), or"
        " as polygons in the Segment task ('polygon')."
    ),
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
    bbox_as: YoloBoundingBoxes,
) -> None:
    """Export the Kili labels of a project to a given format.

    \b
    !!! Info
        The supported formats are:

        - yolo for object detection tasks, the YOLO format the Kili app exports: the bounding
          boxes for Detect, OBB or Segment (`--bbox-as`). yolo_v4, yolo_v5, yolo_v7 and yolo_v8
          are deprecated: use yolo.
        - Kili (a.k.a raw) for all tasks.
        - COCO for object detection tasks (bounding box, polygon and semantic segmentation).
        - Pascal VOC for object detection tasks (bounding box only).
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
            --output-format yolo \\
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
            label_type_in=None,
            include_sent_back_labels=None,
            bbox_as=bbox_as,
        )
    except NoCompatibleJobError as excp:
        print(str(excp))
    except NotCompatibleOptions as excp:
        raise click.UsageError(str(excp)) from excp
