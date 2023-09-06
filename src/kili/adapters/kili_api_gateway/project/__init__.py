"""Mixin extending Kili API Gateway class with Projects related operations."""


import json
from typing import Dict, List, Optional

from kili.adapters.kili_api_gateway.helpers.queries import fragment_builder
from kili.adapters.kili_api_gateway.project.operations import get_project_query
from kili.domain.project import ProjectId
from kili.exceptions import NotFound

from ..base import BaseOperationMixin
from .operations import GQL_CREATE_PROJECT


class ProjectOperationMixin(BaseOperationMixin):
    """Mixin extending Kili API Gateway class with Projects related operations."""

    def get_project(self, project_id: ProjectId, fields: List[str]) -> Dict:
        """Get project fields."""
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
        return ProjectId(result["id"])
