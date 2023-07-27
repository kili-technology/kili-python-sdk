"""Service module for projects."""

from typing import Dict, List

from kili.core.graphql import QueryOptions
from kili.core.graphql.operations.project.queries import ProjectQuery, ProjectWhere
from kili.exceptions import NotFound


def get_project(kili, project_id: str, fields: List[str]) -> Dict:
    """Get a project from its id or raise a NotFound Error if not found."""
    projects = list(
        ProjectQuery(kili.graphql_client, kili.http_client)(
            ProjectWhere(project_id=project_id), fields, QueryOptions(disable_tqdm=True, first=1)
        )
    )
    if len(projects) == 0:
        raise NotFound(
            f"project ID: {project_id}. Maybe your KILI_API_KEY does not belong to a member of the"
            " project."
        )
    return projects[0]


def get_project_field(kili, project_id: str, field: str):
    """Get one project field from a the project id.

    Raise a NotFound Error if the project is not found.
    """
    return get_project(kili, project_id, [field])[field]
