"""Service module for projects"""

from typing import List

from kili.authentication import KiliAuth
from kili.exceptions import NotFound
from kili.graphql import QueryOptions
from kili.graphql.operations.project.queries import ProjectQuery, ProjectWhere


def get_project(auth: KiliAuth, project_id: str, fields: List[str]):
    """Get a project from its id or raise a NotFound Error if not found"""
    projects = list(
        ProjectQuery(auth.client, auth.ssl_verify)(
            ProjectWhere(project_id=project_id), fields, QueryOptions(disable_tqdm=True)
        )
    )
    if len(projects) == 0:
        raise NotFound(
            f"project ID: {project_id}. Maybe your KILI_API_KEY does not belong to a member of the"
            " project."
        )
    return projects[0]


def get_project_field(auth: KiliAuth, project_id: str, field: str):
    """Get one project field from a the project id or raise a NotFound Error
    if the project is not found
    """
    return get_project(auth, project_id, [field])[field]
