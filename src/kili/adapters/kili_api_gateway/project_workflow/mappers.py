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
            "creates": [update_step_mapper(step, data.null_fields) for step in data.create_steps]
            if data.create_steps
            else [],
            "updates": [update_step_mapper(step, data.null_fields) for step in data.update_steps]
            if data.update_steps
            else [],
            "deletes": data.delete_steps or [],
        },
    }


def update_step_mapper(
    data: WorkflowStepCreate | WorkflowStepUpdate,
    null_fields: frozenset[str] = frozenset(),
) -> dict:
    """Build the GraphQL StepData variable to be sent in an operation.

    A field is included when its value is not None, or when its GQL name appears in
    null_fields (meaning the caller explicitly wants to send null to clear that field).
    Fields absent from the TypedDict are never included.
    """
    mapping = {
        "id": "id",
        "name": "name",
        "consensusCoverage": "consensus_coverage",
        "numberOfExpectedLabelsForConsensus": "number_of_expected_labels_for_consensus",
        "stepCoverage": "step_coverage",
        "type": "type",
        "assignees": "assignees",
        "sendBackStepId": "send_back_step_id",
    }
    return {
        gql_key: data[py_key]
        for gql_key, py_key in mapping.items()
        if py_key in data and (data[py_key] is not None or gql_key in null_fields)
    }


def add_review_step_input_mapper(data: AddReviewStepInput) -> dict:
    """Build the GraphQL AddReviewStepInput variable."""
    result: dict = {
        "projectId": data.project_id,
        "name": data.step_name,
        "assignees": data.assignees,
    }
    if data.step_coverage is not None:
        result["stepCoverage"] = data.step_coverage
    if data.use_honeypot is not None:
        result["useHoneypot"] = data.use_honeypot
    if data.send_back_to_step is not None:
        result["sendBackStepId"] = data.send_back_to_step
    return result


def update_labeling_step_properties_input_mapper(data: UpdateLabelingStepPropertiesInput) -> dict:
    """Build the GraphQL UpdateLabelingStepPropertiesInput variable."""
    result: dict = {
        "projectId": data.project_id,
        "stepId": data.step_id,
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
        "stepId": data.step_id,
    }
    if data.assignees is not None:
        result["assignees"] = data.assignees
    if data.step_coverage is not None:
        result["stepCoverage"] = data.step_coverage
    if data.send_back_to_step is not None:
        result["sendBackStepId"] = data.send_back_to_step
    if data.use_honeypot is not None:
        result["useHoneypot"] = data.use_honeypot
    return result


def delete_step_input_mapper(data: DeleteStepInput) -> dict:
    """Build the GraphQL DeleteStepInput variable."""
    return {
        "projectId": data.project_id,
        "stepId": data.step_id,
    }


def rename_step_input_mapper(data: RenameStepInput) -> dict:
    """Build the GraphQL RenameStepInput variable."""
    return {
        "projectId": data.project_id,
        "stepId": data.step_id,
        "newName": data.new_name,
    }
