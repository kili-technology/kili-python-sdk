"""Mixin extending Kili API Gateway class with Projects related operations."""


import json
from typing import Dict, Generator, Optional

from kili.adapters.kili_api_gateway.helpers.queries import (
    PaginatedGraphQLQuery,
    QueryOptions,
    fragment_builder,
    get_number_of_elements_to_query,
)
from kili.adapters.kili_api_gateway.project.operations import get_projects_query
from kili.domain.project import ProjectFilters, ProjectId
from kili.domain.types import ListOrTuple
from kili.exceptions import NotFound

from ..base import BaseOperationMixin
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
        return projects[0]

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
        nb_elements_to_query = get_number_of_elements_to_query(
            self.graphql_client, GQL_COUNT_PROJECTS, where, options
        )
        return PaginatedGraphQLQuery(self.graphql_client).execute_query_from_paginated_call(
            query, where, options, "Retrieving projects", nb_elements_to_query
        )
