"""Data connection mutations."""

from datetime import datetime
from typing import Dict, List, Optional

from typeguard import typechecked

from kili.authentication import KiliAuth
from kili.exceptions import GraphQLError
from kili.utils.logcontext import for_all_methods, log_call

from ... import services
from ...helpers import format_result
from ...queries.data_integration.queries import (
    GQL_GET_DATA_INTEGRATION_FOLDER_AND_SUBFOLDERS,
)
from .exceptions import AddDataConnectionError
from .queries import GQL_ADD_PROJECT_DATA_CONNECTION


@for_all_methods(log_call, exclude=["__init__"])
class MutationsDataConnection:
    """Set of DataConnection mutations."""

    def __init__(self, auth: KiliAuth):
        """Initializes the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    @typechecked
    def add_cloud_storage_connection(
        self,
        project_id: str,
        cloud_storage_integration_id: str,
        selected_folders: Optional[List[str]] = None,
    ) -> Dict:
        """Connect a cloud storage to a project.

        Args:
            project_id: ID of the project.
            cloud_storage_integration_id: ID of the cloud storage integration.
            selected_folders: List of folders of the data integration to connect to the project.
                If not provided, all folders of the data integration will be connected.

        Returns:
            A dict with the DataConnection ID.
        """
        if selected_folders is None:
            variables = {"dataIntegrationId": cloud_storage_integration_id}
            try:
                result = self.auth.client.execute(
                    GQL_GET_DATA_INTEGRATION_FOLDER_AND_SUBFOLDERS, variables=variables
                )
            except GraphQLError as err:
                raise AddDataConnectionError(
                    f"The data integration with id {cloud_storage_integration_id} is not supported"
                    " in the SDK yet. Use the Kili app to create a data connection instead."
                ) from err
            result = format_result("data", result, None, self.auth.ssl_verify)
            selected_folders = [folder["key"] for folder in result]

        variables = {
            "data": {
                "projectId": project_id,
                "integrationId": cloud_storage_integration_id,
                "isChecking": False,
                "lastChecked": datetime.now().isoformat(sep="T", timespec="milliseconds") + "Z",
                "selectedFolders": selected_folders,
            }
        }
        result = self.auth.client.execute(GQL_ADD_PROJECT_DATA_CONNECTION, variables)
        result = format_result("data", result, None, self.auth.ssl_verify)

        # We trigger data difference computation (same behavior as in the frontend)
        services.compute_differences(self.auth, result["id"])

        return result

    @typechecked
    def synchronize_cloud_storage_connection(
        self,
        cloud_storage_connection_id: str,
        delete_extraneous_files: bool = False,
    ) -> Dict:
        """Synchronize a cloud storage connection.

        This method will compute differences between the cloud storage connection and the project
            and then validate the differences.

        If `delete_extraneous_files` is True, it will also delete files that are not in the
            cloud storage integration anymore but that are still in the project.

        Args:
            cloud_storage_connection_id: ID of the cloud storage connection.
            delete_extraneous_files: If True, delete extraneous files.

        Returns:
            A dict with the DataConnection ID.
        """
        return services.synchronize_data_connection(
            self.auth, cloud_storage_connection_id, delete_extraneous_files
        )
