"""CLI's project label subcommand"""

import json
import os
import warnings
from typing import Optional, Tuple

import click

from kili.cli.common_args import Arguments, Options, from_csv
from kili.cli.helpers import (
    check_exclusive_options,
    collect_from_csv,
    get_external_id_from_file_path,
    get_kili_client,
)
from kili.exceptions import NotFound
from kili.helpers import get_file_paths_to_upload
from kili.mutations.label.helpers import generate_create_predictions_arguments


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
    help="Tells to import labels as predictions, which means that they will appear "
    "as pre-annotations in the Kili interface",
)
@click.option(
    "--model-name",
    type=str,
    help="Name of the model that generated predictions, " "if labels are sent as predictions",
)
@Options.verbose
# pylint: disable=too-many-arguments, too-many-locals
def import_labels(
    api_key: Optional[str],
    endpoint: Optional[str],
    files: Optional[Tuple[str, ...]],
    csv_path: str,
    project_id: str,
    is_prediction: bool,
    model_name: str,
    verbose: bool,
):
    """
    Import labels or predictions

    Files can be paths to files or to folders. You can provide several paths separated by spaces.
    The labels to import have to be in the Kili format and stored in a json file.
    File's name must be equal to asset's external_id.

    If no files are provided, --from-csv can be used to import
    assets from a CSV file with two columns:
    - `external_id`: external id for which you want to import labels.
    - `json_response_path`: paths to the json files containing the json_response to upload.

    \b
    !!! Examples "CSV file template"
        ```
        external_id,json_response_path
        asset1,./labels/label_asset1.json
        asset2,./labels/label_asset2.json
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

    """
    if is_prediction and model_name is None:
        raise ValueError(
            "When importing labels as prediction, "
            "you must provide a model name with the --model-name option"
        )

    check_exclusive_options(csv_path, files)

    kili = get_kili_client(api_key=api_key, api_endpoint=endpoint)

    if kili.count_projects(project_id=project_id) == 0:
        raise NotFound(f"project ID: {project_id}")

    if len(files) > 0:
        label_paths = get_file_paths_to_upload(files, lambda path: path.endswith(".json"), verbose)
        if len(label_paths) == 0:
            raise ValueError(
                "No label files to upload. " "Check that the paths exist and file types are .json"
            )
        external_ids = [get_external_id_from_file_path(path) for path in label_paths]

    elif csv_path is not None:

        labels_to_add = collect_from_csv(
            csv_path=csv_path,
            required_columns=["external_id", "json_response_path"],
            optional_columns=[],
            type_check_function=type_check_label,
        )

        if len(labels_to_add) == 0:
            raise ValueError(f"No json files were found in csv: {csv_path}")

        label_paths = [label["json_response_path"] for label in labels_to_add]
        external_ids = [label["external_id"] for label in labels_to_add]

    asset_in_project_external_ids = kili.assets(
        project_id=project_id, fields=["externalId"], disable_tqdm=True
    )
    asset_in_project_external_ids = set(
        asset["externalId"] for asset in asset_in_project_external_ids
    )

    label_index_to_import = []
    for i, external_id in enumerate(external_ids):
        if external_id in asset_in_project_external_ids:
            label_index_to_import.append(i)
        else:
            warnings.warn(f"{external_id} is not an asset of project ID: {project_id}.")

    if is_prediction:
        create_predictions_arguments = generate_create_predictions_arguments(
            [label_paths[i] for i in label_index_to_import],
            [external_ids[i] for i in label_index_to_import],
            model_name,
            project_id,
        )
        kili.create_predictions(**create_predictions_arguments)
        print(f"{len(external_ids)} labels have been successfully imported")

    else:
        for i in label_index_to_import:
            with open(label_paths[i], encoding="utf-8") as label_file:
                json_response = json.load(label_file)

            kili.append_to_labels(
                label_asset_external_id=external_ids[i],
                json_response=json_response,
                project_id=project_id,
            )

    print(f"{len(label_index_to_import)} labels have been successfully imported")
