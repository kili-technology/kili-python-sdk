"""
Helpers for the label mutations
"""
import json
from os import PathLike
from typing import Dict, List, Optional

from kili.exceptions import IncompatibleArgumentsError, MissingArgumentError


def generate_create_predictions_arguments(
    label_paths: List[PathLike],
    external_id_array: List[str],
    model_name: str,
    project_id: str,
) -> Dict:
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


def check_asset_identifier_arguments(
    project_id: Optional[str],
    asset_id_array: Optional[List[str]],
    asset_external_id_array: Optional[List[str]],
):
    "Check that a list of assets can be identified either by their asset ids or their external Ids"
    if asset_id_array is not None:
        if asset_external_id_array is not None:
            raise IncompatibleArgumentsError(
                "Either provide asset ids or asset external ids. Not Both at the same time"
            )
        return True
    if project_id is None or asset_external_id_array is None:
        raise MissingArgumentError(
            "Either provide asset_id_array or project_id and asset_external_id_array"
        )
    return True
