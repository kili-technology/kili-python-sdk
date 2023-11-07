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
from kili.core.enums import ProjectType
from kili.domain.project import ComplianceTag, InputType, ProjectFilters, ProjectId
from kili.domain.types import ListOrTuple

from .common import get_project
from .mappers import project_data_mapper, project_where_mapper
from .operations import (
    GQL_COUNT_PROJECTS,
    GQL_CREATE_PROJECT,
    get_update_properties_in_project_mutation,
)
from .types import ProjectDataKiliAPIGatewayInput


class ProjectOperationMixin(BaseOperationMixin):
    """Mixin extending Kili API Gateway class with Projects related operations."""

    def get_project(self, project_id: ProjectId, fields: ListOrTuple[str]) -> Dict:
        """Get project."""
        return get_project(self.graphql_client, project_id, fields)

    # pylint: disable=too-many-arguments
    def create_project(
        self,
        input_type: InputType,
        json_interface: Dict,
        title: str,
        description: str,
        project_type: Optional[ProjectType],
        compliance_tags: Optional[ListOrTuple[ComplianceTag]],
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
        # complience tags are only available for Kili app > 2.138
        if compliance_tags:
            variables["data"]["complianceTags"] = compliance_tags

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

    def count_projects(self, project_filters: ProjectFilters) -> int:
        """Return the number of projects."""
        where = project_where_mapper(filters=project_filters)
        variables = {"where": where}
        result = self.graphql_client.execute(GQL_COUNT_PROJECTS, variables)
        return result["data"]

    def update_properties_in_project(
        self,
        project_id: ProjectId,
        project_data: ProjectDataKiliAPIGatewayInput,
        fields: ListOrTuple[str],
    ) -> Dict:
        """Update properties in a project."""
        fragment = fragment_builder(fields)
        mutation = get_update_properties_in_project_mutation(fragment)
        data = project_data_mapper(data=project_data)

        # complience tags are only available for Kili app > 2.138
        if "complianceTags" in data and data["complianceTags"] is None:
            del data["complianceTags"]

        variables = {"data": data, "where": {"id": project_id}}
        result = self.graphql_client.execute(mutation, variables)
        return load_project_json_fields(result["data"], fields)
