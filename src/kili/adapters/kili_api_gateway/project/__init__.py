"""Mixin extending Kili API Gateway class with Projects related operations."""


import json
from typing import Dict, Generator, Optional

from kili.adapters.kili_api_gateway.base import BaseOperationMixin
from kili.adapters.kili_api_gateway.helpers.queries import (
    PaginatedGraphQLQuery,
    QueryOptions,
    fragment_builder,
)
from kili.adapters.kili_api_gateway.project.formatters import (
    PROJECT_JSON_FIELDS,
    load_project_json_fields,
)
from kili.adapters.kili_api_gateway.project.operations import get_projects_query
from kili.domain.project import ProjectFilters, ProjectId
from kili.domain.types import ListOrTuple
from kili.exceptions import NotFound

from .mappers import project_where_mapper
from .operations import GQL_COUNT_PROJECTS, GQL_CREATE_PROJECT


class ProjectOperationMixin(BaseOperationMixin):
    """Mixin extending Kili API Gateway class with Projects related operations."""

    def get_project(self, project_id: ProjectId, fields: ListOrTuple[str]) -> Dict:
        """Get project fields."""
        fragment = fragment_builder(fields)
        query = get_projects_query(fragment)
        result = self.graphql_client.execute(
            query=query, variables={"where": {"id": project_id}, "first": 1, "skip": 0}
        )
        projects = result["data"]
        if len(projects) == 0:
            raise NotFound(
                f"project ID: {project_id}. The project does not exist or you do not have access"
                " to it."
            )
        return load_project_json_fields(projects[0], fields)

    # pylint: disable=too-many-arguments
    def create_project(
        self,
        input_type: str,
        json_interface: dict,
        title: str,
        description: str,
        project_type: Optional[str],
    ) -> ProjectId:
        """Create a project."""
        variables = {
            "data": {
                "description": description,
                "inputType": input_type,
                "jsonInterface": json.dumps(json_interface),
                "projectType": project_type,
                "title": title,
            }
        }
        result = self.graphql_client.execute(GQL_CREATE_PROJECT, variables)
        return ProjectId(result["data"]["id"])

    def list_projects(
        self,
        project_filters: ProjectFilters,
        fields: ListOrTuple[str],
        options: QueryOptions,
    ) -> Generator[Dict, None, None]:
        """Return a generator of projects that match the filter."""
        fragment = fragment_builder(fields)
        query = get_projects_query(fragment)
        where = project_where_mapper(filters=project_filters)
        projects_gen = PaginatedGraphQLQuery(self.graphql_client).execute_query_from_paginated_call(
            query, where, options, "Retrieving projects", GQL_COUNT_PROJECTS
        )
        if any(json_field in fields for json_field in PROJECT_JSON_FIELDS):
            projects_gen = (load_project_json_fields(project, fields) for project in projects_gen)
        return projects_gen
