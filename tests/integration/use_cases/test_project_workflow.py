from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.adapters.kili_api_gateway.project_workflow.types import (
    ProjectWorkflowDataKiliAPIGatewayInput,
)
from kili.domain.project import ProjectId
from kili.use_cases.project_workflow import ProjectWorkflowUseCases


def test_given_a_project_workflow_when_update_it_then_it_updates_project_workflow_props(
    kili_api_gateway: KiliAPIGateway,
):
    # Given
    def mocked_update_project_workflow(
        project_id: ProjectId,
        project_workflow_data: ProjectWorkflowDataKiliAPIGatewayInput,
    ):
        return {
            "enforce_step_separation": project_workflow_data.enforce_step_separation,
            "project_id": project_id,
            "steps": {
                "creates": [],
                "deletes": [],
                "updates": [],
            },
        }

    kili_api_gateway.update_project_workflow.side_effect = mocked_update_project_workflow

    # When
    project = ProjectWorkflowUseCases(kili_api_gateway).update_project_workflow(
        project_id=ProjectId("fake_proj_id"),
        enforce_step_separation=False,
    )

    # Then
    assert project == {
        "enforce_step_separation": False,
        "project_id": "fake_proj_id",
        "steps": {
            "creates": [],
            "deletes": [],
            "updates": [],
        },
    }
