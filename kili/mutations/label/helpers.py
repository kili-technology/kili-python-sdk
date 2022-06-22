"""
Helpers for the label mutations
"""
import json
from typing import List
from os import PathLike
import csv


def read_import_label_csv(csv_path: PathLike) -> dict:
    """
    Read a csv file containing external_ids and paths to json_response files for label uploads
    Args:
        csv_path: path to the csv file to read
    """
    with open(csv_path, encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=";")
        # pylint: disable=unnecessary-comprehension
        row_dict = [row for row in reader]
    if sorted(list(row_dict[0].keys())) != ['external_id', 'json_response_path']:
        raise ValueError(
            "The given csv file should have two columns 'external_id' and 'json_response_path'. "
            "Type `kili project label --help` to see the documentation")
    return row_dict


def generate_create_predictions_arguments(
        label_paths: List[PathLike],
        external_id_array: List[str],
        model_name: str,
        project_id,
        verbose: bool) -> dict:
    """
    Generate the arguments of create prediction mutation given
    a list of external ids and paths to json response files

    Args:
        label_paths: a list of paths to json files storing label responses
        external_id_array: a list of external ids
        model_name: the model name
        project_id: Project ID
        verbose: whether to show logs
    """
    json_response_array = []
    filtered_external_id_array = external_id_array.copy()
    for index, path in enumerate(label_paths):
        external_id = external_id_array[index]
        try:
            with open(path, encoding='utf-8') as label_file:
                json_response = json.load(label_file)
                json_response_array.append(json_response)
        except (json.decoder.JSONDecodeError, FileNotFoundError):
            del filtered_external_id_array[index]
            if verbose:
                print(f'{external_id:30} SKIPPED')
    if verbose and len(filtered_external_id_array) != len(external_id_array):
        print(
            "json response file for the above assets were not found or couldn't be decoded")
    return {'project_id': project_id,
            'json_response_array': json_response_array,
            'model_name_array': [model_name]*len(filtered_external_id_array),
            'external_id_array': filtered_external_id_array}
