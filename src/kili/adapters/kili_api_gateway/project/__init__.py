"""Mixin extending Kili API Gateway class with Project related operations."""


from typing import Dict, List

from kili.adapters.kili_api_gateway.helpers.queries import fragment_builder
from kili.adapters.kili_api_gateway.project.operations import get_project_query
from kili.core.graphql.graphql_client import GraphQLClient
from kili.domain.project import ProjectId
from kili.exceptions import NotFound


class ProjectOperationMixin:
    """Mixin extending Kili API Gateway class with Assets related operations."""

    graphql_client: GraphQLClient

    def get_project(self, project_id: ProjectId, fields: List[str]) -> Dict:
        """List assets with given options."""
        fragment = fragment_builder(fields)
        query = get_project_query(fragment)
        result = self.graphql_client.execute(
            query=query, variables={"where": {"id": project_id}, "first": 1, "skip": 0}
        )
        projects = result["data"]
        if len(projects) == 0:
            raise NotFound(
                f"project ID: {project_id}. The project does not exist or you do not have access"
                " to it."
            )
        return projects[0]
