"""Data connection mutations."""

from datetime import datetime
from typing import Dict

from typeguard import typechecked

from kili.authentication import KiliAuth

from ... import services
from ...helpers import format_result
from .queries import GQL_ADD_PROJECT_DATA_CONNECTION


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
                "selectedFolders": [],
            }
        }
        result = self.auth.client.execute(GQL_ADD_PROJECT_DATA_CONNECTION, variables)
        result = format_result("data", result)

        # We trigger data difference computation (same as in the UI)
        services.verify_diff_computed(self.auth, project_id, result["id"])

        return result

    @typechecked
    def synchronize_data_connection(
        self, project_id: str, data_connection_id: str, delete_extraneous_files: bool = False
    ) -> Dict:
        """Synchronize a data connection.

        This method will compute differences between the data connection and the project
            and then validate the differences.

        If `delete_extraneous_files` is True, it will also delete files that are not in the
            data integration anymore but that are still in the project.

        Args:
            project_id: ID of the project.
            data_connection_id: ID of the data connection.
            delete_extraneous_files: If True, delete extraneous files.

        Returns:
            A dict with the DataConnection ID.
        """
        return services.synchronize_data_connection(
            self.auth, project_id, data_connection_id, delete_extraneous_files
        )
