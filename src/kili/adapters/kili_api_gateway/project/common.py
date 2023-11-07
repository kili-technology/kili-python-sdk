"""Project gateway common."""
from typing import Dict

from kili.adapters.kili_api_gateway.helpers.queries import (
    fragment_builder,
)
from kili.adapters.kili_api_gateway.project.formatters import (
    load_project_json_fields,
)
from kili.adapters.kili_api_gateway.project.operations import get_projects_query
from kili.core.graphql.graphql_client import GraphQLClient
from kili.domain.project import ProjectId
from kili.domain.types import ListOrTuple
from kili.exceptions import NotFound


def get_project(
    graphql_client: GraphQLClient, project_id: ProjectId, fields: ListOrTuple[str]
) -> Dict:
    """Get project."""
    fragment = fragment_builder(fields)
    query = get_projects_query(fragment)
    result = graphql_client.execute(
        query=query, variables={"where": {"id": project_id}, "first": 1, "skip": 0}
    )
    projects = result["data"]

    if len(projects) == 0:
        raise NotFound(
            f"project ID: {project_id}. The project does not exist or you do not have access"
            " to it."
        )
    return load_project_json_fields(projects[0], fields)
