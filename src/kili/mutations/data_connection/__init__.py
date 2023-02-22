"""Data connection mutations."""

import logging
from datetime import datetime
from typing import Dict

from typeguard import typechecked

from kili.authentication import KiliAuth

from ...helpers import format_result
from .queries import (
    GQL_ADD_PROJECT_DATA_CONNECTION,
    GQL_COMPUTE_DATA_CONNECTION_DIFFERENCES,
    GQL_DATA_CONNECTION_QUERY,
    GQL_DATA_CONNECTION_UPDATED_SUBSCRIPTION,
    GQL_VALIDATE_DATA_DIFFERENCES,
)


class MutationsDataConnection:
    """Set of DataConnection mutations."""

    def __init__(self, auth: KiliAuth):
        """Initializes the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    @typechecked
    def add_data_connection(self, project_id: str, data_integration_id: str) -> Dict:
        """Connect a remote storage to a project.

        Args:
            project_id: ID of the project.
            data_integration_id: ID of the data integration.

        Returns:
            A dict with the DataConnection ID.
        """
        variables = {
            "data": {
                "projectId": project_id,
                "integrationId": data_integration_id,
                "isChecking": False,
                "lastChecked": datetime.now().isoformat(sep="T", timespec="milliseconds") + "Z",
            }
        }
        result = self.auth.client.execute(GQL_ADD_PROJECT_DATA_CONNECTION, variables)
        return format_result("data", result)

    @typechecked
    def synchronize_data_connection(
        self, data_connection_id: str, delete_extraneous_files: bool = False
    ) -> Dict:
        """Synchronize a data connection.

        Args:
            data_connection_id: ID of the data connection.
            delete_extraneous_files: If True, delete extraneous files.

        Returns:
            A dict with the DataConnection ID.
        """
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        logger.addHandler(logging.StreamHandler())
        logger.info("Synchronizing data connection: %s", data_connection_id)

        variables = {"where": {"id": data_connection_id}}
        result = self.auth.client.execute(GQL_DATA_CONNECTION_QUERY, variables)
        data_connection = format_result("data", result)

        # TODO
        variables = {"projectID": data_connection["projectId"]}
        subscription = self.auth.client.subscribe(
            GQL_DATA_CONNECTION_UPDATED_SUBSCRIPTION, variables
        )
        # compute differences if not already computing
        if not data_connection["isChecking"]:
            variables = {"where": {"id": data_connection_id}}
            result = self.auth.client.execute(GQL_COMPUTE_DATA_CONNECTION_DIFFERENCES, variables)
            data_connection = format_result("data", result)

        for result in subscription:
            print(result)

        # check differences
        variables = {"where": {"id": data_connection_id}}
        result = self.auth.client.execute(GQL_DATA_CONNECTION_QUERY, variables)
        data_connection = format_result("data", result)
        assert not data_connection["isChecking"], data_connection
        added = data_connection["dataDifferencesSummary"]["added"]
        removed = data_connection["dataDifferencesSummary"]["removed"]
        total = data_connection["dataDifferencesSummary"]["total"]
        nb_assets = data_connection["numberOfAssets"]

        logger.info("Found %d assets in the data connection.", nb_assets)
        logger.info("Found %d differences.", total)

        if total == 0:
            logger.info("No differences found. Nothing to synchronize.")
            return data_connection

        # validate differences
        if removed > 0 and delete_extraneous_files:
            variables = {
                "where": {"connectionId": data_connection_id, "type": "REMOVE"},
                "processingParameters": None,
            }
            result = self.auth.client.execute(GQL_VALIDATE_DATA_DIFFERENCES, variables)
            data_connection = format_result("data", result)
            logger.info("Removed %d extraneous files.", removed)

        variables = {
            "where": {"connectionId": data_connection_id, "type": "ADD"},
            "processingParameters": None,
        }
        result = self.auth.client.execute(GQL_VALIDATE_DATA_DIFFERENCES, variables)
        data_connection = format_result("data", result)
        logger.info("Added %d files.", added)

        return data_connection
