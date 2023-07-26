"""Project version mutations."""

from typing import Optional

from typeguard import typechecked

from kili.authentication import KiliAuth
from kili.utils.logcontext import for_all_methods, log_call

from ...helpers import format_result
from .queries import GQL_UPDATE_PROPERTIES_IN_PROJECT_VERSION


@for_all_methods(log_call, exclude=["__init__"])
class MutationsProjectVersion:  # pylint: disable=too-few-public-methods
    """Set of ProjectVersion mutations."""

    def __init__(self, auth: KiliAuth):
        """Initialize the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    @typechecked
    def update_properties_in_project_version(self, project_version_id: str, content: Optional[str]):
        """Update properties of a project version.

        Args:
            project_version_id: Identifier of the project version
            content: Link to download the project version

        Returns:
            A result object which indicates if the mutation was successful.

        Examples:
            >>> kili.update_properties_in_project_version(
                    project_version_id=project_version_id,
                    content='test')
        """
        variables = {
            "content": content,
            "id": project_version_id,
        }
        result = self.auth.client.execute(GQL_UPDATE_PROPERTIES_IN_PROJECT_VERSION, variables)
        return format_result("data", result, None, self.auth.ssl_verify)
