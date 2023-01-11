"""Service module for projects"""

from typing import Dict, List, cast

from kili.exceptions import NotFound
from kili.graphql import QueryOptions
from kili.graphql.operations.project.queries import ProjectQuery, ProjectWhere


def get_project(kili, project_id: str, fields: List[str]):
    """Get a project from its id or raise a NotFound Error if not found"""
    projects = cast(
        List[Dict],
        ProjectQuery(kili.auth.client)(
            ProjectWhere(project_id=project_id), fields, QueryOptions(disable_tqdm=True)
        ),
    )
    if len(projects) == 0:
        raise NotFound(
            f"project ID: {project_id}. Maybe your KILI_API_KEY does not belong to a member of the"
            " project."
        )
    return projects[0]


def get_project_field(kili, project_id: str, field: str):
    """Get one project field from a the project id or raise a NotFound Error
    if the project is not found
    """
    return get_project(kili, project_id, [field])[field]
