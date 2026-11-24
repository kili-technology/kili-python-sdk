"""Tests for kili.projects.workflow.steps."""

from unittest.mock import MagicMock

import pytest
import pytest_mock

from kili.domain_api.project_workflow import WorkflowNamespace
from kili.utils.logcontext import LogContext
from tests.unit.domain_api.project_workflow_fakes import (
    MULTI_GROUP_PROJECT,
    MULTI_STEP_PROJECT,
    FakeWorkflowServer,
    assignees,
    gateway_of,
)

NEW_REVIEW = {
    "id": "review-new",
    "name": "Second review",
    "type": "REVIEW",
    "stepGroupId": "group-2",
    "assignees": assignees("reviewer"),
}
NEW_LABELING_STEP = {
    "id": "label-new",
    "name": "Labeling",
    "type": "DEFAULT",
    "stepGroupId": "group-1",
    "assignees": assignees("labeler"),
}


def steps_of(server: FakeWorkflowServer):
    return WorkflowNamespace(MagicMock(), gateway_of(server)).steps


def answer_with(*steps: dict) -> dict:
    return {"steps": [*MULTI_GROUP_PROJECT["steps"], *steps]}


def test_list_answers_the_steps():
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT)

    steps = steps_of(server).list(project_id="project")

    assert [step["id"] for step in steps] == ["label-1", "review-1", "label-2", "review-2"]
    assert "assignees{" in server.queries[0]


def test_create_adds_a_review_through_add_review_step():
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT, answer=answer_with(NEW_REVIEW))

    step = steps_of(server).create(
        project_id="project",
        name="Second review",
        assignees=["reviewer@acme.com"],
        group_name="Experts",
        sample_percentage=20,
        send_back_to_step="review-1",
        use_honeypot=True,
    )

    assert step == NEW_REVIEW
    assert server.mutation == (
        "addReviewStep",
        {
            "projectId": "project",
            "name": "Second review",
            "assignees": ["reviewer"],
            "stepCoverage": 20,
            "useHoneypot": True,
            "sendBackStepId": "review-1",
            "stepGroupId": "group-2",
        },
    )


def test_create_resolves_the_send_back_target_over_the_whole_project():
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT, answer=answer_with(NEW_REVIEW))

    steps_of(server).create(
        project_id="project",
        name="Second review",
        assignees=["reviewer@acme.com"],
        group_name="Experts",
        sample_percentage=20,
        send_back_to_step={"name": "Labeling", "group_name": "Team"},
    )

    assert server.mutation[1]["sendBackStepId"] == "label-1"


def test_create_adds_a_review_to_the_only_group_of_a_multi_step_project():
    new_review = {**NEW_REVIEW, "stepGroupId": "default"}
    server = FakeWorkflowServer(
        MULTI_STEP_PROJECT, answer={"steps": [*MULTI_STEP_PROJECT["steps"], new_review]}
    )

    step = steps_of(server).create(
        project_id="project",
        name="Second review",
        assignees=["reviewer@acme.com"],
        sample_percentage=0,
    )

    assert step == new_review
    assert "stepGroupId" not in server.mutation[1]
    assert server.mutation[1]["stepCoverage"] == 0


def test_create_needs_the_group_when_the_project_has_several():
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT)

    with pytest.raises(ValueError, match="several groups: give the group_name"):
        steps_of(server).create(
            project_id="project",
            name="Second review",
            assignees=["reviewer@acme.com"],
            sample_percentage=20,
        )


def test_create_needs_the_sample_percentage_of_a_review():
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT)

    with pytest.raises(ValueError, match="sample_percentage is required to create a review"):
        steps_of(server).create(
            project_id="project",
            name="Second review",
            assignees=["reviewer@acme.com"],
            group_name="Experts",
        )


def test_create_refuses_consensus_on_a_review():
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT)

    with pytest.raises(ValueError, match="Consensus is set on a labeling step"):
        steps_of(server).create(
            project_id="project",
            name="Second review",
            assignees=["reviewer@acme.com"],
            group_name="Experts",
            sample_percentage=20,
            consensus_coverage=50,
        )


def test_create_adds_a_labeling_step_through_the_workflow_settings(
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch("kili.use_cases.project_workflow.steps.cuid", return_value="label-new")
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT, answer=answer_with(NEW_LABELING_STEP))

    step = steps_of(server).create(
        project_id="project",
        name="Labeling",
        assignees=["labeler@acme.com"],
        group_name="Team",
        type="DEFAULT",
        consensus_coverage=50,
        number_of_expected_labels_for_consensus=2,
    )

    assert step == NEW_LABELING_STEP
    name, sent = server.mutation
    assert name == "editProjectWorkflowSettings"
    assert "stepGroups" not in sent
    assert sent["steps"]["creates"] == [
        {
            "id": "label-new",
            "name": "Labeling",
            "type": "DEFAULT",
            "assignees": ["labeler"],
            "stepGroupId": "group-1",
            "consensusCoverage": 50,
            "numberOfExpectedLabelsForConsensus": 2,
        }
    ]


@pytest.mark.parametrize(
    ("parameter", "message"),
    [
        ({"sample_percentage": 20}, "sample_percentage is set on a review"),
        ({"send_back_to_step": "label-1"}, "send_back_to_step is set on a review"),
        ({"use_honeypot": True}, "use_honeypot cannot be given at a labeling step's creation"),
    ],
)
def test_create_refuses_on_a_labeling_step_what_belongs_to_a_review(parameter, message):
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT)

    with pytest.raises(ValueError, match=message):
        steps_of(server).create(
            project_id="project",
            name="Labeling",
            assignees=["labeler@acme.com"],
            group_name="Team",
            type="DEFAULT",
            **parameter,
        )


def test_update_sends_every_change_in_one_call():
    updated = {**MULTI_GROUP_PROJECT["steps"][3], "name": "Senior review"}
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT, answer={"steps": [updated]})

    step = steps_of(server).update(
        project_id="project",
        step={"name": "Expert review", "group_name": "Experts"},
        name="Senior review",
        use_honeypot=False,
        send_back_to_step={"name": "Labeling", "group_name": "Team"},
    )

    assert step == updated
    name, sent = server.mutation
    assert name == "editProjectWorkflowSettings"
    assert sent["steps"]["updates"] == [
        {
            "id": "review-2",
            "name": "Senior review",
            "sendBackStepId": "label-1",
            "useHoneypot": False,
        }
    ]


def test_update_finds_a_step_by_a_name_no_other_step_has():
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT, answer=MULTI_GROUP_PROJECT)

    steps_of(server).update(project_id="project", step="Expert review", use_honeypot=True)

    assert server.mutation[1]["steps"]["updates"] == [{"id": "review-2", "useHoneypot": True}]


def test_update_sends_the_consensus_of_a_labeling_step():
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT, answer=MULTI_GROUP_PROJECT)

    steps_of(server).update(
        project_id="project",
        step="label-1",
        consensus_coverage=40,
        number_of_expected_labels_for_consensus=3,
    )

    assert server.mutation[1]["steps"]["updates"] == [
        {"id": "label-1", "consensusCoverage": 40, "numberOfExpectedLabelsForConsensus": 3}
    ]


def test_update_refuses_a_name_several_groups_use():
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT)

    with pytest.raises(ValueError, match="Multiple steps named 'Labeling'"):
        steps_of(server).update(project_id="project", step="Labeling", name="Label")


def test_update_refuses_consensus_on_a_review():
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT)

    with pytest.raises(ValueError, match="step 'Review' is a review"):
        steps_of(server).update(project_id="project", step="review-1", consensus_coverage=50)


def test_update_refuses_a_send_back_target_on_a_labeling_step():
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT)

    with pytest.raises(ValueError, match="step 'Labeling' is a labeling step"):
        steps_of(server).update(project_id="project", step="label-1", send_back_to_step="label-2")


def test_update_refuses_a_call_that_changes_nothing():
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT)

    with pytest.raises(ValueError, match="at least one property"):
        steps_of(server).update(project_id="project", step="review-1")


def test_delete_sends_the_step_by_id():
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT, answer=MULTI_GROUP_PROJECT)

    deleted = steps_of(server).delete(
        project_id="project", step={"name": "Labeling", "group_name": "Experts"}
    )

    assert deleted == {"id": "label-2"}
    assert server.mutation[1]["steps"] == {"creates": [], "updates": [], "deletes": ["label-2"]}


def test_a_step_method_names_itself_by_its_path_in_the_log_context():
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT, answer=MULTI_GROUP_PROJECT)

    steps_of(server).delete(project_id="project", step="review-1")

    assert LogContext()["kili-client-method-name"] == "projects.workflow.steps.delete"
