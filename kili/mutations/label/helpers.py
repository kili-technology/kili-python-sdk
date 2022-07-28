"""
Helpers for the label mutations
"""
import json
from os import PathLike
from typing import List


def generate_create_predictions_arguments(
    label_paths: List[PathLike],
    external_id_array: List[str],
    model_name: str,
    project_id: str,
) -> dict:
    """
    Generate the arguments of create prediction mutation given
    a list of external ids and paths to json response files

    Args:
        label_paths: a list of paths to json files storing label responses
        external_id_array: a list of external ids
        model_name: the model name
        project_id: Project ID
    """
    json_response_array = []
    for path in label_paths:
        with open(path, encoding="utf-8") as label_file:
            json_response = json.load(label_file)
            json_response_array.append(json_response)
    return {
        "project_id": project_id,
        "json_response_array": json_response_array,
        "model_name_array": [model_name] * len(external_id_array),
        "external_id_array": external_id_array,
    }
