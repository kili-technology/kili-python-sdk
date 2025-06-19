"""GraphQL payload data mappers for project operations."""

from typing import Dict, Union

from kili.domain.project import WorkflowStepCreate, WorkflowStepUpdate

from .types import ProjectWorkflowDataKiliAPIGatewayInput


def project_input_mapper(data: ProjectWorkflowDataKiliAPIGatewayInput) -> Dict:
    """Build the GraphQL ProjectWorfklowData variable to be sent in an operation."""
    return {
        "enforceStepSeparation": data.enforce_step_separation,
        "steps": {
            "creates": [update_step_mapper(step) for step in data.create_steps]
            if data.create_steps
            else [],
            "updates": [update_step_mapper(step) for step in data.update_steps]
            if data.update_steps
            else [],
            "deletes": data.delete_steps if data.delete_steps else [],
        },
    }


def update_step_mapper(data: Union[WorkflowStepCreate, WorkflowStepUpdate]) -> Dict:
    """Build the GraphQL create StepData variable to be sent in an operation."""
    step = {
        "id": data["id"] if "id" in data else None,
        "name": data["name"] if "name" in data else None,
        "consensusCoverage": data["consensus_coverage"] if "consensus_coverage" in data else None,
        "numberOfExpectedLabelsForConsensus": data["number_of_expected_labels_for_consensus"]
        if "number_of_expected_labels_for_consensus" in data
        else None,
        "order": data["order"] if "order" in data else None,
        "stepCoverage": data["step_coverage"] if "step_coverage" in data else None,
        "type": data["type"] if "type" in data else None,
        "assignees": data["assignees"] if "assignees" in data else None,
    }
    return {k: v for k, v in step.items() if v is not None}


def step_data_mapper(data: Dict) -> Dict:
    """Build the GraphQL StepData variable to be sent in an operation."""
    return {
        "id": data["id"],
        "name": data["name"],
        "type": data["type"],
    }
