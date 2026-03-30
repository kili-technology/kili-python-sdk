"""GraphQL payload data mappers for project operations."""

from kili.domain.project import WorkflowStepCreate, WorkflowStepUpdate

from .types import ProjectWorkflowDataKiliAPIGatewayInput


def project_input_mapper(data: ProjectWorkflowDataKiliAPIGatewayInput) -> dict:
    """Build the GraphQL ProjectWorfklowData variable to be sent in an operation."""
    return {
        "enforceStepSeparation": data.enforce_step_separation,
        "steps": {
            "creates": [
                update_step_mapper(step, for_copy=data.for_copy) for step in data.create_steps
            ]
            if data.create_steps
            else [],
            "updates": [
                update_step_mapper(step, for_copy=data.for_copy) for step in data.update_steps
            ]
            if data.update_steps
            else [],
            "deletes": data.delete_steps if data.delete_steps else [],
        },
    }


def update_step_mapper(
    data: WorkflowStepCreate | WorkflowStepUpdate, for_copy: bool = False
) -> dict:
    """Build the GraphQL create StepData variable to be sent in an operation."""
    ## In copy worklow use case, we want to copy as well
    # consensusCoverage and numberOfExpectedLabelsForConsensus properties, even if they are None

    step = {
        "id": data.get("id"),
        "name": data.get("name"),
        "consensusCoverage": data.get("consensus_coverage"),
        "numberOfExpectedLabelsForConsensus": data.get("number_of_expected_labels_for_consensus"),
        "stepCoverage": data.get("step_coverage"),
        "type": data.get("type"),
        "assignees": data.get("assignees"),
        "sendBackStepId": data.get("send_back_step_id"),
    }
    if for_copy:
        special_keys = ["consensusCoverage", "numberOfExpectedLabelsForConsensus"]
        return {k: v for k, v in step.items() if v is not None or k in special_keys}
    return {k: v for k, v in step.items() if v is not None}
