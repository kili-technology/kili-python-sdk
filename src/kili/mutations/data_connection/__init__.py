"""Data connection mutations."""

from datetime import datetime
from typing import Dict

from typeguard import typechecked

from kili.authentication import KiliAuth

from ...helpers import format_result
from .queries import GQL_ADD_PROJECT_DATA_CONNECTION


# pylint: disable=too-few-public-methods
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
            project_id : ID of the project
            data_integration_id : ID of the data integration

        Returns:
            A result object which indicates if the mutation was successful, or an error message.
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
