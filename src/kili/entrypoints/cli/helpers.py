"""CLI's common helpers functions."""

import csv
import warnings
from typing import Any, Callable, Dict, List, Optional

from kili.adapters.http_client import HttpClient
from kili.client import Kili
from kili.core.graphql.graphql_client import GraphQLClientName


def get_kili_client(api_key: Optional[str], api_endpoint: Optional[str]):
    """Instantiate a kili client for the CLI functions."""
    return Kili(api_key=api_key, api_endpoint=api_endpoint, client_name=GraphQLClientName.CLI)


def dict_type_check(
    dict_: Dict[str, Any],
    type_check: Callable[[str, str, Optional[HttpClient]], str],
    http_client: Optional[HttpClient],
):
    """Check if elements in row have correct type and return [row]."""
    warnings_message = ""
    for key, value in dict_.items():
        warnings_message += type_check(key, value, http_client)
    if len(warnings_message) == 0:
        return [dict_]

    warnings.warn(
        f"{warnings_message} {next(iter(dict_.values()))}  will not be added.", stacklevel=2
    )
    return []


def collect_from_csv(
    csv_path: str,
    required_columns: List[str],
    optional_columns: List[str],
    type_check_function: Callable[[str, str, Optional[HttpClient]], str],
    http_client: Optional[HttpClient] = None,
):
    """Read a csv to collect required_columns and optional_columns."""
    out = []
    with open(csv_path, encoding="utf-8") as csv_file:
        csvreader = csv.DictReader(csv_file)
        headers = csvreader.fieldnames
        if not headers:
            headers = []

        missing_columns = list(set(required_columns) - set(headers))
        if len(missing_columns) > 0:
            raise ValueError(f"{missing_columns} must be headers of the csv file: {csv_path}")
        for row in csvreader:
            out += dict_type_check(
                dict_={k: v for k, v in row.items() if k in required_columns + optional_columns},
                type_check=type_check_function,
                http_client=http_client,
            )

    return out
