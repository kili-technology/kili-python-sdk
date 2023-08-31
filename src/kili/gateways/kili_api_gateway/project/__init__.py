"""Mixin extending Kili API Gateway class with Project related operations."""


from typing import List

from kili.core.graphql.graphql_client import GraphQLClient
from kili.exceptions import NotFound
from kili.gateways.kili_api_gateway.helpers.queries import fragment_builder
from kili.gateways.kili_api_gateway.project.operations import get_project_query
from kili.gateways.kili_api_gateway.project.types import ProjectWhere


class ProjectOperationMixin:
    """Mixin extending Kili API Gateway class with Assets related operations."""

    graphql_client: GraphQLClient

    def get_project(
        self,
        project_id,
        fields: List[str],
    ):
        """List assets with given options."""
        fragment = fragment_builder(fields)
        query = get_project_query(fragment)
        where = ProjectWhere(project_id=project_id)
        result = self.graphql_client.execute(
            query=query, variables={"where": where.build_gql_where(), "first": 1}
        )
        projects = result["data"]
        if len(projects) == 0:
            raise NotFound(
                f"project ID: {project_id}. Maybe your KILI_API_KEY does not belong to a member of"
                " the project."
            )
        return projects[0]
