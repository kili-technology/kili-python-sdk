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


def test_add_review_step(kili_api_gateway: KiliAPIGateway):
    # Given
    def mocked_add_review_step(data):
        return {
            "steps": [
                {
                    "id": "fake_id",
                    "name": data.step_name,
                },
            ],
        }

    kili_api_gateway.add_review_step.side_effect = mocked_add_review_step

    # When
    project = ProjectWorkflowUseCases(kili_api_gateway).add_review_step(
        project_id=ProjectId("fake_proj_id"),
        step_name="test",
        assignees=["test+fake@kili-technology.com"],
        step_coverage=100,
    )

    # Then
    assert project == {
        "steps": [
            {
                "id": "fake_id",
                "name": "test",
            },
        ],
    }


def test_rename_step(kili_api_gateway: KiliAPIGateway):
    # Given
    kili_api_gateway.get_steps.return_value = [
        {"id": "step_1", "name": "Label"},
        {"id": "step_2", "name": "Old review"},
    ]

    def mocked_rename_step(data):
        return {
            "steps": [
                {"id": "step_1", "name": "Label"},
                {"id": data.step_id, "name": data.new_name},
            ]
        }

    kili_api_gateway.rename_step.side_effect = mocked_rename_step

    # When
    result = ProjectWorkflowUseCases(kili_api_gateway).rename_step(
        project_id="fake_proj_id",
        step_name="Old review",
        new_name="New review",
    )

    # Then
    assert result == {
        "steps": [{"id": "step_1", "name": "Label"}, {"id": "step_2", "name": "New review"}]
    }


def test_delete_last_step(kili_api_gateway: KiliAPIGateway):
    # Given
    kili_api_gateway.get_steps.return_value = [
        {"id": "step_1", "name": "Label"},
        {"id": "step_2", "name": "Review 1"},
        {"id": "step_3", "name": "Review 2"},
    ]

    def mocked_delete_step(data):
        assert str(data.project_id) == "fake_proj_id"
        assert data.step_id == "step_3"

        return {"steps": [{"id": "step_1", "name": "Label"}, {"id": "step_2", "name": "Review 1"}]}

    kili_api_gateway.delete_step.side_effect = mocked_delete_step

    # When
    result = ProjectWorkflowUseCases(kili_api_gateway).delete_last_step(
        project_id="fake_proj_id",
    )

    # Then
    assert result == {
        "steps": [{"id": "step_1", "name": "Label"}, {"id": "step_2", "name": "Review 1"}]
    }


def test_update_labeling_step_properties(kili_api_gateway: KiliAPIGateway):
    # Given
    kili_api_gateway.get_steps.return_value = [
        {"id": "step_1", "name": "Label"},
        {"id": "step_2", "name": "Review"},
    ]

    def mocked_update_labeling_step_properties(data):
        assert str(data.project_id) == "fake_proj_id"
        assert data.step_id == "step_1"
        assert data.consensus_coverage == 80
        assert data.number_of_expected_labels_for_consensus == 3
        assert data.use_honeypot is True

        return {
            "steps": [
                {"id": "step_1", "name": "Label"},
                {"id": "step_2", "name": "Review"},
            ]
        }

    kili_api_gateway.update_labeling_step_properties.side_effect = (
        mocked_update_labeling_step_properties
    )

    # When
    result = ProjectWorkflowUseCases(kili_api_gateway).update_labeling_step_properties(
        project_id="fake_proj_id",
        step_name="Label",
        consensus_coverage=80,
        number_of_expected_labels_for_consensus=3,
        use_honeypot=True,
    )

    # Then
    assert result == {
        "steps": [
            {"id": "step_1", "name": "Label"},
            {"id": "step_2", "name": "Review"},
        ]
    }


def test_update_review_step_properties(kili_api_gateway: KiliAPIGateway):
    # Given
    kili_api_gateway.get_steps.return_value = [
        {"id": "step_1", "name": "Label"},
        {"id": "step_2", "name": "Review"},
    ]

    def mocked_update_review_step_properties(data):
        assert str(data.project_id) == "fake_proj_id"
        assert data.step_id == "step_2"
        assert data.assignees == ["test+fake@kili-technology.com"]
        assert data.step_coverage == 100
        assert data.send_back_to_step == "Label"
        assert data.use_honeypot is False

        return {
            "steps": [
                {"id": "step_1", "name": "Label"},
                {"id": "step_2", "name": "Review"},
            ]
        }

    kili_api_gateway.update_review_step_properties.side_effect = (
        mocked_update_review_step_properties
    )

    # When
    result = ProjectWorkflowUseCases(kili_api_gateway).update_review_step_properties(
        project_id="fake_proj_id",
        step_name="Review",
        assignees=["test+fake@kili-technology.com"],
        step_coverage=100,
        send_back_to_step="Label",
        use_honeypot=False,
    )

    # Then
    assert result == {
        "steps": [
            {"id": "step_1", "name": "Label"},
            {"id": "step_2", "name": "Review"},
        ]
    }
