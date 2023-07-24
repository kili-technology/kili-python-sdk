"""Services for data connections."""
import logging
import time
from typing import Any, Dict, List, Literal

from tenacity import Retrying
from tenacity.retry import retry_if_exception_type
from tenacity.stop import stop_after_delay
from tenacity.wait import wait_exponential

from kili.core.graphql import QueryOptions
from kili.core.graphql.operations.asset.queries import AssetQuery, AssetWhere
from kili.core.graphql.operations.data_connection.queries import (
    DataConnectionIdWhere,
    DataConnectionQuery,
)
from kili.core.helpers import format_result
from kili.entrypoints.mutations.data_connection.queries import (
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


def get_data_connection(kili, data_connection_id: str, fields: List[str]) -> Dict:
    """Get data connection information."""
    where = DataConnectionIdWhere(data_connection_id=data_connection_id)
    options = QueryOptions(first=1, disable_tqdm=True)
    data_connection = list(
        DataConnectionQuery(kili.graphql_client, kili.http_client)(where, fields, options)
    )
    if len(data_connection) == 0:
        raise ValueError(f"No data connection with id {data_connection_id}")
    return data_connection[0]


def trigger_validate_data_differences(
    kili, diff_type: Literal["ADD", "REMOVE"], data_connection_id: str
) -> Dict:
    """Call the validateDataDifferences resolver."""
    variables = {
        "where": {"connectionId": data_connection_id, "type": diff_type},
        "processingParameters": None,
    }
    result = kili.graphql_client.execute(GQL_VALIDATE_DATA_DIFFERENCES, variables)
    data_connection = format_result("data", result, None, kili.http_client)
    return data_connection


def validate_data_differences(
    kili, diff_type: Literal["ADD", "REMOVE"], data_connection: Dict
) -> None:
    """Call the validateDataDifferences resolver and wait until the validation is done."""
    diff = data_connection["dataDifferencesSummary"]["added" if diff_type == "ADD" else "removed"]

    where = AssetWhere(project_id=data_connection["projectId"])
    nb_assets_before = AssetQuery(kili.graphql_client, kili.http_client).count(where)

    trigger_validate_data_differences(kili, diff_type, data_connection["id"])

    for attempt in Retrying(
        wait=wait_exponential(multiplier=1, min=1, max=4),
        stop=stop_after_delay(5 * 60),
        retry=retry_if_exception_type(ValueError),
        reraise=True,
    ):
        with attempt:
            nb_assets_after = AssetQuery(kili.graphql_client, kili.http_client).count(where)
            if abs(nb_assets_after - nb_assets_before) != diff:
                raise ValueError(
                    "Number of assets in project after validation is not correct: before"
                    f" {nb_assets_before} assets, after {nb_assets_after} assets,"
                    f" dataDifferencesSummary diff {diff}"
                )


def compute_differences(kili, data_connection_id: str) -> Dict:
    """Compute the data connection differences."""
    logger = _get_logger()
    logger.info("Computing the data connection differences.")

    data_connection = get_data_connection(
        kili,
        data_connection_id,
        fields=[
            "dataIntegration.azureIsUsingServiceCredentials",
            "dataIntegration.platform",
            "dataIntegration.azureSASToken",
            "dataIntegration.azureConnectionURL",
            "dataIntegration.id",
            "selectedFolders",
        ],
    )

    data_integration = data_connection["dataIntegration"]

    blob_paths = None

    # for azure using credentials, it is required to provide the blob paths to compute the diffs
    if (
        data_integration["platform"] == "Azure"
        and data_integration["azureIsUsingServiceCredentials"]
    ):
        logger.info("Azure data integration is using service credentials. Retrieving blob paths.")
        if not (data_integration["azureSASToken"] and data_integration["azureConnectionURL"]):
            raise ValueError(
                f"Cannot compute differences for data connection {data_connection_id} with data"
                f" integration {data_integration['id']}. Need to provide \"azureSASToken\" and"
                f' "azureConnectionURL" in data integration: {data_integration}'
            )

        try:
            # pylint: disable=import-outside-toplevel
            from .azure import (
                get_blob_paths_azure_data_connection_with_service_credentials,
            )
        except ImportError as err:
            raise ImportError(
                "The azure-storage-blob package is required to use Azure buckets. "
                " Run `pip install kili[azure]` to install it."
            ) from err

        blob_paths = get_blob_paths_azure_data_connection_with_service_credentials(
            data_connection=data_connection, data_integration=data_integration
        )

    variables: Dict[str, Any] = {"where": {"id": data_connection_id}}
    if blob_paths is not None:
        variables["data"] = {"blobPaths": blob_paths}
    result = kili.graphql_client.execute(GQL_COMPUTE_DATA_CONNECTION_DIFFERENCES, variables)
    data_connection = format_result("data", result, None, kili.http_client)
    return data_connection


def verify_diff_computed(kili, data_connection_id: str) -> None:
    """Verify that the data connection differences have been computed.

    Trigger the computation if not already computing.
    """
    logger = _get_logger()
    logger.info("Verifying that the data connection differences have been computed.")

    data_connection = get_data_connection(kili, data_connection_id, fields=["isChecking"])

    if not data_connection["isChecking"]:
        compute_differences(kili, data_connection_id)
        time.sleep(1)  # backend needs some time to refresh the "isChecking"

    for attempt in Retrying(
        wait=wait_exponential(multiplier=1, min=1, max=4),
        stop=stop_after_delay(5 * 60),
        retry=retry_if_exception_type(ValueError),
        reraise=True,
    ):
        with attempt:
            data_connection = get_data_connection(kili, data_connection_id, fields=["isChecking"])
            if data_connection["isChecking"]:
                raise ValueError(f"Data connection is still checking: {data_connection}")

    time.sleep(1)  # backend needs some time to refresh the "isChecking"


def synchronize_data_connection(
    kili, data_connection_id: str, delete_extraneous_files: bool, dry_run: bool
) -> Dict:
    """Launch a data connection synchronization."""
    logger = _get_logger()
    logger.info("Synchronizing data connection: %s", data_connection_id)

    verify_diff_computed(kili, data_connection_id)

    data_connection = get_data_connection(
        kili,
        data_connection_id,
        fields=[
            "id",
            "dataDifferencesSummary.added",
            "dataDifferencesSummary.removed",
            "dataDifferencesSummary.total",
            "isChecking",
            "numberOfAssets",
            "projectId",
        ],
    )
    if data_connection["isChecking"]:
        raise ValueError(f"Data connection should not be checking: {data_connection}")

    added = data_connection["dataDifferencesSummary"]["added"]
    removed = data_connection["dataDifferencesSummary"]["removed"]
    total = data_connection["dataDifferencesSummary"]["total"]
    nb_assets = data_connection["numberOfAssets"]

    logger.info("Currently %d asset(s) imported from the data connection.", nb_assets)

    if total == 0:
        logger.info("No differences found. Nothing to synchronize.")
        return data_connection

    logger.info(
        "Found %d difference(s): %d asset(s) to add, %d asset(s) to remove.", total, added, removed
    )

    if dry_run:
        # pylint: disable=unnecessary-lambda-assignment
        validate_data_differences_func = lambda *args, **kwargs: None  # noqa: E731
        logger.info("Dry run: no data will be added or removed.")
    else:
        validate_data_differences_func = validate_data_differences

    if removed > 0:
        if delete_extraneous_files:
            validate_data_differences_func(kili, "REMOVE", data_connection)
            logger.info("Removed %d extraneous file(s).", removed)
        else:
            logger.info(
                "Use delete_extraneous_files=True to remove %d extraneous file(s).",
                removed,
            )

    if added > 0:
        validate_data_differences_func(kili, "ADD", data_connection)
        logger.info("Added %d file(s).", added)

    return get_data_connection(kili, data_connection_id, fields=["numberOfAssets", "projectId"])
