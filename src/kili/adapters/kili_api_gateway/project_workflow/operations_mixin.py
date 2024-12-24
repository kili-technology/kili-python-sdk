"""Mixin extending Kili API Gateway class with Projects related operations."""

from typing import Dict

from kili.adapters.kili_api_gateway.base import BaseOperationMixin
from kili.adapters.kili_api_gateway.helpers.queries import (
    fragment_builder,
)
from kili.domain.project import ProjectId

from .mappers import project_input_mapper
from .operations import (
    get_update_project_workflow_mutation,
)
from .types import ProjectWorkflowDataKiliAPIGatewayInput


class ProjectWorkflowOperationMixin(BaseOperationMixin):
    """Mixin extending Kili API Gateway class with Projects workflow related operations."""

    def update_project_workflow(
        self,
        project_id: ProjectId,
        project_workflow_data: ProjectWorkflowDataKiliAPIGatewayInput,
    ) -> Dict:
        """Update properties in a project workflow."""
        project_workflow_input = project_input_mapper(data=project_workflow_data)

        fields = tuple(name for name, val in project_workflow_input.items() if val is not None)
        fragment = fragment_builder(fields)
        mutation = get_update_project_workflow_mutation(fragment)

        project_workflow_input["projectId"] = project_id

        variables = {"input": project_workflow_input}
        result = self.graphql_client.execute(mutation, variables)
        return result["data"]
