"""
Helpers for the label mutations
"""
import glob
import json
import os
from typing import List, Tuple
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


def get_label_file_paths_to_upload(files: Tuple[str, ...], verbose: bool) -> List[str]:
    """Get a list of paths for the label files to upload given a list of files or folder paths.

    Args:
        files: a list path that can either be file paths, folder paths or unexisting paths

    Returns:
        a list of the paths of the label files to upload.
    """
    file_paths = []
    for item in files:
        if os.path.isfile(item):
            file_paths.append(item)
        elif os.path.isdir(item):
            folder_path = os.path.join(item, "")
            file_paths.extend(
                [sub_item for sub_item in glob.glob(folder_path + "*") if os.path.isfile(sub_item)]
            )
        else:
            file_paths.extend(
                [sub_item for sub_item in glob.glob(item) if os.path.isfile(sub_item)]
            )

    file_paths_to_upload = [path for path in file_paths if path.endswith(".json")]
    if len(file_paths_to_upload) == 0:
        raise ValueError(
            "No files to upload. " "Check that the paths exist and that the file is .json"
        )
    if verbose:
        for path in file_paths:
            if path not in file_paths_to_upload:
                print(f"{path:30} SKIPPED")
        if len(file_paths_to_upload) != len(file_paths):
            print("Paths skipped either do not exist " "or point towards a non -json file")
    file_paths_to_upload.sort()
    return file_paths_to_upload
