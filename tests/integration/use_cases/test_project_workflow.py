import pytest

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.adapters.kili_api_gateway.project_workflow.common import resolve_step
from kili.adapters.kili_api_gateway.project_workflow.types import (
    ProjectWorkflowDataKiliAPIGatewayInput,
)
from kili.domain.project import ProjectId
from kili.use_cases.project_workflow import ProjectWorkflowUseCases

# Two groups using the same step names: a name alone designates no step.
TWO_GROUP_WORKFLOW = {
    "workflowVersion": "V3",
    "stepGroups": [{"id": "group_1", "name": "Team 1"}, {"id": "group_2", "name": "Team 2"}],
    "steps": [
        {"id": "step_1", "name": "Label", "stepGroupId": "group_1"},
        {"id": "step_2", "name": "Review", "stepGroupId": "group_1"},
        {"id": "step_3", "name": "Label", "stepGroupId": "group_2"},
        {"id": "step_4", "name": "Review", "stepGroupId": "group_2"},
        {"id": "step_5", "name": "Old review", "stepGroupId": "group_2"},
    ],
}


def given_the_two_group_workflow(kili_api_gateway):
    kili_api_gateway.get_step.side_effect = (
        lambda project_id, step_id=None, step_name=None, group_name=None: resolve_step(
            TWO_GROUP_WORKFLOW, step_id, step_name, group_name
        )
    )


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
    given_the_two_group_workflow(kili_api_gateway)

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
        "steps": [{"id": "step_1", "name": "Label"}, {"id": "step_5", "name": "New review"}]
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
    given_the_two_group_workflow(kili_api_gateway)

    def mocked_update_labeling_step_properties(data):
        assert str(data.project_id) == "fake_proj_id"
        assert data.step_id == "step_3"
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
        group_name="Team 2",
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
    given_the_two_group_workflow(kili_api_gateway)

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
        step_id="step_2",
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


@pytest.mark.parametrize(
    ("step_designation", "error"),
    [
        ({"step_name": "Review"}, "Multiple steps named 'Review'"),
        ({"step_id": "step_2", "step_name": "Review"}, "not both"),
        ({}, "not both"),
        ({"step_id": "step_2", "group_name": "Team 1"}, "group_name goes with step_name only"),
        ({"step_id": "unknown"}, "Step 'unknown' not found"),
    ],
)
def test_a_step_is_designated_either_by_id_or_by_name_and_group(
    kili_api_gateway: KiliAPIGateway, step_designation: dict, error: str
):
    # Given
    given_the_two_group_workflow(kili_api_gateway)

    # When / Then
    with pytest.raises(ValueError, match=error):
        ProjectWorkflowUseCases(kili_api_gateway).rename_step(
            project_id="fake_proj_id", new_name="New name", **step_designation
        )


def test_update_project_workflow_sends_the_steps_given_by_name_by_id(
    kili_api_gateway: KiliAPIGateway,
):
    # Given
    given_the_two_group_workflow(kili_api_gateway)
    kili_api_gateway.get_project_workflow_context.return_value = TWO_GROUP_WORKFLOW

    # When
    ProjectWorkflowUseCases(kili_api_gateway).update_project_workflow(
        project_id=ProjectId("fake_proj_id"),
        update_steps=[
            {"name": "Review", "group_name": "Team 2", "step_coverage": 50},
            {"id": "step_1", "name": "Renamed label"},
        ],
        delete_steps=["step_5", "Old review", {"name": "Label", "group_name": "Team 2"}, "step_3"],
    )

    # Then
    data = kili_api_gateway.update_project_workflow.call_args[0][1]
    assert data.update_steps == [
        {"id": "step_4", "name": "Review", "step_coverage": 50},
        {"id": "step_1", "name": "Renamed label"},
    ]
    # Given twice, by id and by name, a step is deleted once.
    assert data.delete_steps == ["step_5", "step_3"]


@pytest.mark.parametrize(
    ("update_steps", "delete_steps", "error"),
    [
        ([{"name": "Review"}], None, "Multiple steps named 'Review'"),
        ([{"id": "step_2", "group_name": "Team 1"}], None, "group_name goes with a step given"),
        ([{"step_coverage": 50}], None, "given by its id, or by its name"),
        (None, ["Review"], "Multiple steps named 'Review'"),
    ],
)
def test_update_project_workflow_refuses_a_step_it_cannot_tell_apart(
    kili_api_gateway: KiliAPIGateway, update_steps, delete_steps, error: str
):
    given_the_two_group_workflow(kili_api_gateway)
    kili_api_gateway.get_project_workflow_context.return_value = TWO_GROUP_WORKFLOW

    with pytest.raises(ValueError, match=error):
        ProjectWorkflowUseCases(kili_api_gateway).update_project_workflow(
            project_id=ProjectId("fake_proj_id"),
            update_steps=update_steps,
            delete_steps=delete_steps,
        )
