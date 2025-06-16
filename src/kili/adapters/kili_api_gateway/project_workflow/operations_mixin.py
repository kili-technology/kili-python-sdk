"""Mixin extending Kili API Gateway class with Projects related operations."""

from typing import Dict, List

from kili.adapters.kili_api_gateway.base import BaseOperationMixin
from kili.adapters.kili_api_gateway.helpers.queries import (
    fragment_builder,
)
from kili.domain.project import ProjectId
from kili.exceptions import NotFound

from .mappers import project_input_mapper, step_data_mapper
from .operations import (
    GQL_GET_STEPS,
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

        fields = tuple(
            name
            for name, val in project_workflow_input.items()
            if val is not None and name != "steps"
        )
        fragment = fragment_builder(fields)
        mutation = get_update_project_workflow_mutation(fragment)

        project_workflow_input["projectId"] = project_id

        variables = {"input": project_workflow_input}
        result = self.graphql_client.execute(mutation, variables)
        return result["data"]

    def get_steps(
        self,
        project_id: ProjectId,
    ) -> List[Dict]:
        """Get steps in a project workflow."""
        variables = {"where": {"id": project_id}, "first": 1, "skip": 0}
        result = self.graphql_client.execute(GQL_GET_STEPS, variables)
        project = result["data"]

        if len(project) == 0:
            raise NotFound(f"project ID: {project_id}. The project does not exist.")

        steps = project[0].get("steps")

        if len(steps) == 0:
            raise NotFound(
                f"project ID: {project_id}. The workflow v2 is not activated on this project."
            )
        steps_mapper = step_data_mapper(steps)

        return [step for step in steps_mapper if step.get("isActivated") is True]
