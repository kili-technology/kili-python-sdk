"""GraphQL payload data mappers for project operations."""

from kili.domain.project import WorkflowStepCreate, WorkflowStepUpdate

from .types import ProjectWorkflowDataKiliAPIGatewayInput


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
