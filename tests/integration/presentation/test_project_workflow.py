import pytest_mock

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.adapters.kili_api_gateway.project_workflow.operations import (
    get_update_project_workflow_mutation,
)
from kili.presentation.client.project_workflow import ProjectWorkflowClientMethods
from kili.use_cases.project_workflow import ProjectWorkflowUseCases


def test_when_updating_project_workflow_then_it_returns_updated_project_workflow(
    mocker: pytest_mock.MockerFixture,
):
    kili = ProjectWorkflowClientMethods()
    kili.kili_api_gateway = KiliAPIGateway(
        graphql_client=mocker.MagicMock(), http_client=mocker.MagicMock()
    )
    # Given
    project_id = "fake_proj_id"

    # When
    kili.update_project_workflow(project_id, enforce_step_separation=False)

    # Then
    kili.kili_api_gateway.graphql_client.execute.assert_called_once_with(
        get_update_project_workflow_mutation(" enforceStepSeparation"),
        {
            "input": {
                "projectId": "fake_proj_id",
                "enforceStepSeparation": False,
                "steps": {
                    "creates": [],
                    "deletes": [],
                    "updates": [],
                },
            },
        },
    )


def test_when_getting_steps_then_it_returns_steps(
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch.object(
        ProjectWorkflowUseCases,
        "get_steps",
        return_value=[{"id": "step_id", "name": "step_name", "type": "step_type"}],
    )
    kili = ProjectWorkflowClientMethods()
    kili.kili_api_gateway = KiliAPIGateway(
        graphql_client=mocker.MagicMock(), http_client=mocker.MagicMock()
    )
    # Given
    project_id = "fake_proj_id"

    # When
    steps = kili.get_steps(project_id)

    # Then

    assert steps == [{"id": "step_id", "name": "step_name", "type": "step_type"}]
