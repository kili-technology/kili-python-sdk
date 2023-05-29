"""Data connection mutations."""

from datetime import datetime
from typing import Dict, List, Optional

from typeguard import typechecked

from kili import services
from kili.core.authentication import KiliAuth
from kili.core.graphql import QueryOptions
from kili.core.graphql.operations.data_integration.queries import (
    DataIntegrationsQuery,
    DataIntegrationWhere,
)
from kili.core.helpers import format_result
from kili.utils.logcontext import for_all_methods, log_call

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
        data_integrations = list(
            DataIntegrationsQuery(self.auth.client)(
                where=DataIntegrationWhere(data_integration_id=cloud_storage_integration_id),
                fields=["id"],
                options=QueryOptions(disable_tqdm=True, first=1, skip=0),
            )
        )
        if len(data_integrations) == 0:
            raise ValueError(
                f"Cloud storage integration with id {cloud_storage_integration_id} not found."
            )

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
        result = format_result("data", result)

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

        This method will compute differences between the cloud storage connection and the project,
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
