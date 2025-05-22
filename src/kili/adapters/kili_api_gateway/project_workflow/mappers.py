"""GraphQL payload data mappers for project operations."""

from typing import Dict

from .types import ProjectWorkflowDataKiliAPIGatewayInput


def project_input_mapper(data: ProjectWorkflowDataKiliAPIGatewayInput) -> Dict:
    """Build the GraphQL ProjectWorfklowData variable to be sent in an operation."""
    return {
        "enforceStepSeparation": data.enforce_step_separation,
    }


def step_data_mapper(data: Dict) -> Dict:
    """Build the GraphQL StepData variable to be sent in an operation."""
    return {
        "id": data["id"],
        "name": data["name"],
        "type": data["type"],
    }
