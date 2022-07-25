"""CLI's project label subcommand"""

import json
import os
from typing import Optional, Tuple
import click

from kili.cli.common_args import Arguments, Options, from_csv
from kili.cli.helpers import collect_from_csv
from kili.client import Kili
from kili.exceptions import NotFound
from kili.mutations.label.helpers import generate_create_predictions_arguments


def type_check_label(key, value):
    """type check value based on key"""
    if key == "json_response_path" and not (os.path.isfile(value) and value.endswith(".json")):
        return f"{value} is not a valid path to a json file, "

    return ""


@click.command()
@Options.api_key
@Options.endpoint
@Arguments.files
@from_csv(['external_id', 'json_response_path'], [])
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
# pylint: disable=too-many-arguments, too-many-locals
def import_labels(
        api_key: Optional[str],
        endpoint: Optional[str],
        files: Optional[Tuple[str, ...]],
        csv_path: str,
        project_id: str,
        is_prediction: bool,
        model_name: str):
    """
    Import labels or predictions

    The labels to import have to be in the Kili format and stored in a json file.
    Labels to import are provided in a CSV file with two columns:
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

    labels_to_add = collect_from_csv(
        csv_path=csv_path,
        required_columns=["external_id", "json_response_path"],
        optional_columns=[],
        type_check_function=type_check_label,
    )

    if len(labels_to_add) == 0:
        raise ValueError(f"No json files were found in csv: {csv_path}")

    kili = Kili(api_key=api_key, api_endpoint=endpoint)

    if kili.count_projects(project_id=project_id) == 0:
        raise NotFound(f"project ID: {project_id}")
    if is_prediction:
        label_paths = [row["json_response_path"] for row in labels_to_add]
        external_id_array = [row["external_id"] for row in labels_to_add]
        create_predictions_arguments = generate_create_predictions_arguments(
            label_paths, external_id_array, model_name, project_id
        )
        kili.create_predictions(**create_predictions_arguments)
        print(f"{len(external_id_array)} labels have been successfully imported")

    else:
        for row in labels_to_add:
            external_id = row["external_id"]
            path = row["json_response_path"]
            with open(path, encoding="utf-8") as label_file:
                json_response = json.load(label_file)

            kili.append_to_labels(
                label_asset_external_id=external_id,
                json_response=json_response,
                project_id=project_id,
            )

        print(f"{len(labels_to_add)} labels have been successfully imported")
