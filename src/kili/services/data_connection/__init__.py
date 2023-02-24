"""
Services for data connections
"""
import logging
import threading
import time
from typing import Dict, List

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
from ...subscriptions.data_connection.subscriptions import (
    GQL_DATA_CONNECTION_UPDATED_SUBSCRIPTION,
)


def get_data_connection(auth: KiliAuth, data_connection_id: str, fields: List[str]) -> Dict:
    """
    Get data connection information
    """
    where = DataConnectionIdWhere(data_connection_id=data_connection_id)
    options = QueryOptions()
    data_connection = next(DataConnectionQuery(auth.client)(where, fields, options))
    return data_connection


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


def compute_differences(auth: KiliAuth, data_connection_id: str) -> Dict:
    """
    Compute differences between the data connection differences (if not already computing)
    """
    data_connection = get_data_connection(
        auth,
        data_connection_id,
        fields=["isChecking"],
    )
    if data_connection["isChecking"]:
        return data_connection

    variables = {"where": {"id": data_connection_id}}
    result = auth.client.execute(GQL_COMPUTE_DATA_CONNECTION_DIFFERENCES, variables)
    data_connection = format_result("data", result)
    return data_connection


def verify_diff_computed(auth: KiliAuth, project_id: str, data_connection_id: str) -> None:
    """
    Verify that the data connection differences have been computed

    Launch a subscription to the data connection and wait until isChecking is False
    """
    subscription = auth.client.subscribe(
        GQL_DATA_CONNECTION_UPDATED_SUBSCRIPTION, {"projectID": project_id}
    )

    # we need to add a delay before compute_differences
    # because the subscription takes time to be ready
    def compute_differences_with_delay(auth: KiliAuth, data_connection_id: str) -> Dict:
        time.sleep(1)
        return compute_differences(auth, data_connection_id)

    thread_launch_comp = threading.Thread(
        target=compute_differences_with_delay,
        args=(auth, data_connection_id),
    )
    thread_launch_comp.start()

    for result in subscription:
        print("result: ", result)  # TODO: remove
        is_computing_diff = result["data"]["isChecking"]
        if not is_computing_diff:
            break

    thread_launch_comp.join()

    time.sleep(1)  # backend needs some time to update the data connection "isChecking"


def synchronize_data_connection(
    auth: KiliAuth, project_id: str, data_connection_id: str, delete_extraneous_files: bool
) -> Dict:
    """
    Launch a data connection synchronization
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    logger.info("Synchronizing data connection: %s", data_connection_id)

    verify_diff_computed(auth, project_id, data_connection_id)

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
