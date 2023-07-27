"""Project version mutations."""

from typing import Dict, Optional

from typeguard import typechecked

from kili.core.graphql.graphql_client import GraphQLClient
from kili.entrypoints.base import BaseOperationEntrypointMixin
from kili.utils.logcontext import for_all_methods, log_call

from .queries import GQL_UPDATE_PROPERTIES_IN_PROJECT_VERSION


@for_all_methods(log_call, exclude=["__init__"])
class MutationsProjectVersion(BaseOperationEntrypointMixin):
    """Set of ProjectVersion mutations."""

    graphql_client: GraphQLClient

    @typechecked
    def update_properties_in_project_version(
        self, project_version_id: str, content: Optional[str]
    ) -> Dict:
        """Update properties of a project version.

        Args:
            project_version_id: Identifier of the project version
            content: Link to download the project version

        Returns:
            A dictionary containing the updated project version.

        Examples:
            >>> kili.update_properties_in_project_version(
                    project_version_id=project_version_id,
                    content='test'
                )
        """
        variables = {
            "content": content,
            "id": project_version_id,
        }
        result = self.graphql_client.execute(GQL_UPDATE_PROPERTIES_IN_PROJECT_VERSION, variables)
        return self.format_result("data", result)
