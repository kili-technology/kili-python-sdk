"""CLI's common helpers functions"""

import csv
import warnings
from typing import Any, Dict, List, Optional

from kili.graphql_client import GraphQLClientName

from ..client import Kili

# pylint: disable=consider-using-f-string


def get_kili_client(api_key: str, api_endpoint: str):
    """Instantiate a kili client for the CLI functions"""
    return Kili(api_key=api_key, api_endpoint=api_endpoint, client_name=GraphQLClientName.CLI)


def dict_type_check(dict_: Dict[str, Any], type_check):
    """check if elements in row have correct type and return [row]"""
    warnings_message = ""
    for key, value in dict_.items():
        warnings_message += type_check(key, value)
    if len(warnings_message) == 0:
        return [dict_]

    warnings.warn(warnings_message + "{} will not be added.".format(list(dict_.values())[0]))
    return []


def collect_from_csv(
    csv_path: str,
    required_columns: List[str],
    optional_columns: Optional[List[str]],
    type_check_function,
):
    """read a csv to collect required_columns and optional_columns"""
    out = []
    with open(csv_path, "r", encoding="utf-8") as csv_file:
        csvreader = csv.DictReader(csv_file)
        headers = csvreader.fieldnames
        missing_columns = list(set(required_columns) - set(headers))
        if len(missing_columns) > 0:
            raise ValueError(f"{missing_columns} must be headers of the csv file: {csv_path}")
        for row in csvreader:
            out += dict_type_check(
                dict_={k: v for k, v in row.items() if k in required_columns + optional_columns},
                type_check=type_check_function,
            )

    return out


def get_external_id_from_file_path(path: str):
    """Return external_id from file's path
    ex: 'tree/leaf/file_name.txt- -> file_name
    """
    file_path = path.split("/")[-1]
    return ".".join(file_path.split(".")[:-1])


def check_exclusive_options(csv_path: Optional[str], files: Optional[List[str]]):
    """Forbid mutual use of options and argument(s)"""

    if (csv_path is not None) + (len(files) > 0) > 1:
        raise ValueError("files arguments and option --from-csv are exclusive.")

    if (csv_path is not None) + (len(files) > 0) == 0:
        raise ValueError("You must either provide file arguments or use the option --from-csv")
