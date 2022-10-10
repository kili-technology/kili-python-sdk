"""CLI's project label subcommand"""


import os
from typing import Optional, Tuple

import click
from typing_extensions import get_args

from kili.cli.common_args import Arguments, Options, from_csv
from kili.cli.helpers import get_kili_client
from kili.services import label_import
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
@from_csv(["external_id", "json_response_path"], [])
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
    default="raw",
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
    files: Optional[Tuple[str, ...]],
    csv_path: str,
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

    Files can be paths to files or to folders. You can provide several paths separated by spaces.
    The labels to import have to be in the Kili format and stored in a json file.
    File's name must be equal to asset's external_id.

    If no files are provided, --from-csv can be used to import
    assets from a CSV file with two columns:

    \b
      - `label_asset_external_id`: external id for which you want to import labels.
      - `label_asset_id`: asset id for which you want to import labels (mutual exclusive with the
    field above, and not available for predictions)
      - `path`: paths to the json files containing the json_response to upload.

    Additional columns can be provided in the CSV file, see `.append_to_labels` in the Python client
    documentation:

    \b
      - label_type
      - seconds_to_label
      - author_id

    \b
    !!! Examples "CSV file template for the raw Kili format"
        ```
        label_asset_external_id,path
        asset1,./labels/label_asset1.json
        asset2,./labels/label_asset2.json
        ```

     \b
    !!! Examples "CSV file template for a Yolo format"
        ```
        label_asset_external_id,path
        asset1,./labels/label_asset1.txt
        asset2,./labels/label_asset2.txt
        ```

    \b
    !!! Examples
        To import default labels:
        ```
        kili project label \\
             dir1/dir2/ dir1/dir3/test1.json \\
            --project-id <project_id>
        ```
        ```
        kili project label \\
            --from-csv path/to/file.csv \\
            --project-id <project_id>
        ```
        To import labels as predictions:
        ```
        kili project label \\
            --from-csv path/to/file.csv \\
            --project-id <project_id> \\
            --prediction \\
            --model-name YOLO-run-3
        ```
        To import labels as predictions in the Yolo v5 format into a target job:
        ```
        kili project label \\
            --from-csv path/to/file.csv \\
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

    label_import.import_labels_from_files(
        kili,
        csv_path,
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
