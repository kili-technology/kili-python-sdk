"""
Services for data connections
"""
import logging
import time
from typing import Any, Dict, List, Optional

from tenacity import Retrying
from tenacity.retry import retry_if_exception_type
from tenacity.stop import stop_after_delay
from tenacity.wait import wait_fixed
from typing_extensions import Literal

from kili.graphql import QueryOptions

from ...authentication import KiliAuth
from ...graphql.operations.data_connection.queries import (
    DataConnectionIdWhere,
    DataConnectionQuery,
)
from ...helpers import format_result
from ...mutations.data_connection.queries import (
    GQL_COMPUTE_DATA_CONNECTION_DIFFERENCES,
    GQL_VALIDATE_DATA_DIFFERENCES,
)

LOGGER = None


def _get_logger() -> logging.Logger:
    global LOGGER  # pylint: disable=global-statement

    if LOGGER is not None:
        return LOGGER

    LOGGER = logging.getLogger(__name__)
    LOGGER.setLevel(logging.INFO)
    LOGGER.addHandler(logging.StreamHandler())
    return LOGGER


def get_data_connection(auth: KiliAuth, data_connection_id: str, fields: List[str]) -> Dict:
    """
    Get data connection information
    """
    where = DataConnectionIdWhere(data_connection_id=data_connection_id)
    options = QueryOptions(first=1, disable_tqdm=True)
    data_connection = list(DataConnectionQuery(auth.client)(where, fields, options))
    if len(data_connection) == 0:
        raise ValueError(f"No data connection with id {data_connection_id}")
    return data_connection[0]


def validate_data_differences(
    auth: KiliAuth, diff_type: Literal["ADD", "REMOVE"], data_connection_id: str
) -> Dict:
    """
    Validate data differences
    """
    variables = {
        "where": {"connectionId": data_connection_id, "type": diff_type},
        "processingParameters": None,
    }
    result = auth.client.execute(GQL_VALIDATE_DATA_DIFFERENCES, variables)
    data_connection = format_result("data", result)
    return data_connection


def compute_differences(
    auth: KiliAuth, data_connection_id: str, blob_paths: Optional[List[str]] = None
) -> Dict:
    """
    Compute the data connection differences
    """
    variables: Dict[str, Any] = {"where": {"id": data_connection_id}}
    if blob_paths is not None:
        variables["data"] = {"blobPaths": blob_paths}
    result = auth.client.execute(GQL_COMPUTE_DATA_CONNECTION_DIFFERENCES, variables)
    data_connection = format_result("data", result)
    return data_connection


def verify_diff_computed(auth: KiliAuth, data_connection_id: str) -> None:
    """
    Verify that the data connection differences have been computed.

    Trigger the computation if not already computing.
    """
    logger = _get_logger()
    logger.info("Verifying that the data connection differences have been computed")

    data_connection = get_data_connection(auth, data_connection_id, fields=["isChecking"])

    if not data_connection["isChecking"]:
        compute_differences(auth, data_connection_id)
        time.sleep(1)  # backend needs some time...

    for attempt in Retrying(
        stop=stop_after_delay(60),
        wait=wait_fixed(1),
        retry=retry_if_exception_type(ValueError),
        reraise=True,
    ):
        with attempt:
            data_connection = get_data_connection(auth, data_connection_id, fields=["isChecking"])
            if data_connection["isChecking"]:
                raise ValueError(f"Data connection is still checking: {data_connection}")

    time.sleep(1)  # backend needs some time...


def synchronize_data_connection(
    auth: KiliAuth, data_connection_id: str, delete_extraneous_files: bool
) -> Dict:
    """
    Launch a data connection synchronization
    """
    logger = _get_logger()
    logger.info("Synchronizing data connection: %s", data_connection_id)

    verify_diff_computed(auth, data_connection_id)

    data_connection = get_data_connection(
        auth,
        data_connection_id,
        fields=[
            "dataDifferencesSummary.added",
            "dataDifferencesSummary.removed",
            "dataDifferencesSummary.total",
            "isChecking",
            "numberOfAssets",
        ],
    )
    if data_connection["isChecking"]:
        raise ValueError(f"Data connection is still checking: {data_connection}")

    added = data_connection["dataDifferencesSummary"]["added"]
    removed = data_connection["dataDifferencesSummary"]["removed"]
    total = data_connection["dataDifferencesSummary"]["total"]
    nb_assets = data_connection["numberOfAssets"]

    logger.info("Found %d asset(s) in the data connection.", nb_assets)

    if total == 0:
        logger.info("No differences found. Nothing to synchronize.")
        return data_connection

    logger.info(
        "Found %d difference(s): %d assets to add, %d assets to remove.", total, added, removed
    )

    if removed > 0:
        if delete_extraneous_files:
            data_connection = validate_data_differences(auth, "REMOVE", data_connection_id)
            logger.info("Removed %d extraneous file(s).", removed)
        else:
            logger.info(
                "Use delete_extraneous_files=True to remove %d extraneous file(s).",
                removed,
            )

    if added > 0:
        data_connection = validate_data_differences(auth, "ADD", data_connection_id)
        logger.info("Added %d file(s).", added)

    return data_connection
