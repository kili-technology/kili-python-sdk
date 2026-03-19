"""GraphQL payload data mappers for project operations."""

from kili.domain.project import WorkflowStepCreate, WorkflowStepUpdate

from .types import (
    AddReviewStepInput,
    DeleteStepInput,
    ProjectWorkflowDataKiliAPIGatewayInput,
    RenameStepInput,
    UpdateLabelingStepPropertiesInput,
    UpdateReviewStepPropertiesInput,
)


def project_input_mapper(data: ProjectWorkflowDataKiliAPIGatewayInput) -> dict:
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
            "deletes": data.delete_steps or [],
        },
    }


def update_step_mapper(data: WorkflowStepCreate | WorkflowStepUpdate) -> dict:
    """Build the GraphQL create StepData variable to be sent in an operation."""
    step = {
        "id": data["id"] if "id" in data else None,
        "name": data["name"] if "name" in data else None,
        "consensusCoverage": data["consensus_coverage"] if "consensus_coverage" in data else None,
        "numberOfExpectedLabelsForConsensus": data["number_of_expected_labels_for_consensus"]
        if "number_of_expected_labels_for_consensus" in data
        else None,
        "stepCoverage": data["step_coverage"] if "step_coverage" in data else None,
        "type": data["type"] if "type" in data else None,
        "assignees": data["assignees"] if "assignees" in data else None,
        "sendBackStepId": data["send_back_step_id"] if "send_back_step_id" in data else None,
    }
    return {k: v for k, v in step.items() if v is not None}


def add_review_step_input_mapper(data: AddReviewStepInput) -> dict:
    """Build the GraphQL AddReviewStepInput variable."""
    result: dict = {
        "projectId": data.project_id,
        "name": data.name,
        "assignees": data.assignees,
    }
    if data.consensus_coverage is not None:
        result["consensusCoverage"] = data.consensus_coverage
    if data.number_of_expected_labels_for_consensus is not None:
        result["numberOfExpectedLabelsForConsensus"] = data.number_of_expected_labels_for_consensus
    if data.step_coverage is not None:
        result["stepCoverage"] = data.step_coverage
    if data.use_honeypot is not None:
        result["useHoneypot"] = data.use_honeypot
    if data.send_back_to_step is not None:
        result["sendBackToStep"] = data.send_back_to_step
    return result


def update_labeling_step_properties_input_mapper(data: UpdateLabelingStepPropertiesInput) -> dict:
    """Build the GraphQL UpdateLabelingStepPropertiesInput variable."""
    result: dict = {
        "projectId": data.project_id,
        "stepName": data.step_name,
    }
    if data.consensus_coverage is not None:
        result["consensusCoverage"] = data.consensus_coverage
    if data.number_of_expected_labels_for_consensus is not None:
        result["numberOfExpectedLabelsForConsensus"] = data.number_of_expected_labels_for_consensus
    if data.use_honeypot is not None:
        result["useHoneypot"] = data.use_honeypot
    return result


def update_review_step_properties_input_mapper(data: UpdateReviewStepPropertiesInput) -> dict:
    """Build the GraphQL UpdateReviewStepPropertiesInput variable."""
    result: dict = {
        "projectId": data.project_id,
        "stepName": data.step_name,
    }
    if data.step_coverage is not None:
        result["stepCoverage"] = data.step_coverage
    if data.send_back_to_step is not None:
        result["sendBackToStep"] = data.send_back_to_step
    if data.use_honeypot is not None:
        result["useHoneypot"] = data.use_honeypot
    return result


def delete_step_input_mapper(data: DeleteStepInput) -> dict:
    """Build the GraphQL DeleteStepInput variable."""
    return {
        "projectId": data.project_id,
        "stepName": data.step_name,
    }


def rename_step_input_mapper(data: RenameStepInput) -> dict:
    """Build the GraphQL RenameStepInput variable."""
    return {
        "projectId": data.project_id,
        "stepName": data.step_name,
        "newName": data.new_name,
    }
