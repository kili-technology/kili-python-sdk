"""CLI's project label subcommand"""


import os
from typing import Optional, Tuple

import click
from typing_extensions import get_args

from kili import services
from kili.cli.common_args import Arguments, Options
from kili.cli.helpers import get_kili_client
from kili.services.label_import.types import LabelFormat


def type_check_label(key, value):
    """type check value based on key"""
    if key == "json_response_path" and not (os.path.isfile(value) and value.endswith(".json")):
        return f"{value} is not a valid path to a json file, "

    return ""


@click.command(name="label")
@Options.api_key
@Options.endpoint
@Arguments.files
@Options.project_id
@click.option(
    "--prediction",
    "is_prediction",
    type=bool,
    is_flag=True,
    default=False,
    help=(
        "Tells to import labels as predictions, which means that they will appear "
        "as pre-annotations in the Kili interface"
    ),
)
@click.option(
    "--model-name",
    type=str,
    help="Name of the model that generated predictions, if labels are sent as predictions",
)
@Options.verbose
@click.option(
    "--input-format",
    type=click.Choice(get_args(LabelFormat)),
    help="Format in which the labels are encoded",
    default="kili",
    show_default='"raw" kili format',
)
@click.option(
    "--metadata-file",
    type=str,
    help="File containing format metadata (if relevant to the input format)",
)
@click.option(
    "--target-job",
    type=str,
    help="Job name in the project where to upload the labels (if relevant to the input format)",
)
# pylint: disable=too-many-arguments, too-many-locals
def import_labels(
    api_key: Optional[str],
    endpoint: Optional[str],
    files: Tuple[str, ...],
    project_id: str,
    is_prediction: bool,
    model_name: Optional[str],
    verbose: bool,
    input_format: str,
    metadata_file: Optional[str],
    target_job: Optional[str],
):
    """
    Import labels or predictions

    Files can be paths to files or to folders. <br>
    You can provide several paths separated by spaces.
    Label files are JSON files containing labels in the Kili format: the value corresponding to the
    jsonResponse field of a label
    (see [here](https://docs.kili-technology.com/reference/export-classification) for example).<br>
    File's name must be equal to asset's external_id.

    \b
    !!! Examples
        To import default labels:
        ```
        kili project label \\
            dir/labels/ dir/ground-truth/image1.json \\
            --project-id <project_id>
        ```
        To import labels as predictions:
        ```
        kili project label \\
            dir/predictions/ \\
            --project-id <project_id> \\
            --prediction \\
            --model-name YOLO-run-3
        ```
        To import labels as predictions in the Yolo v5 format into a target job:
        ```
        kili project label \\
            dir/predictions/ \\
            --project-id <project_id> \\
            --prediction \\
            --model-name YOLO-v5 \\
            --metadata-file classes.yml \\
            --target-job IMAGE_DETECTION_JOB \\
            --input-format yolo_v5
        ```


    """
    if is_prediction and model_name is None:
        raise ValueError(
            "When importing labels as prediction, "
            "you must provide a model name with the --model-name option"
        )

    kili = get_kili_client(api_key=api_key, api_endpoint=endpoint)

    services.import_labels_from_files(
        kili,
        list(files or []),
        metadata_file,
        project_id,
        input_format,
        target_job,
        not verbose,
        "INFO" if verbose else "WARNING",
        model_name,
        is_prediction,
    )
