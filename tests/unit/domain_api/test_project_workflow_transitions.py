"""Tests for kili.projects.workflow.transitions and the transition lists of workflow.update."""

from typing import Any
from unittest.mock import MagicMock

import pytest
import pytest_mock

from kili.domain_api.project_workflow import WorkflowNamespace
from kili.exceptions import GraphQLError
from kili.utils.logcontext import LogContext
from tests.unit.domain_api.project_workflow_fakes import (
    MULTI_GROUP_PROJECT,
    FakeWorkflowServer,
    gateway_of,
)


def condition(type_: str, **fields: Any) -> dict:
    return {
        "type": type_,
        "percentage": None,
        "jobName": None,
        "categories": None,
        "quantifier": None,
        "value": None,
        **fields,
    }


def transition(id_: str, priority: int, cond: dict, **ends: Any) -> dict:
    return {
        "id": id_,
        "fromStepId": None,
        "fromStepGroupId": None,
        "toStepId": None,
        "priority": priority,
        "condition": cond,
        **ends,
    }


STORED = [
    transition(
        "into-review-1",
        1,
        condition("SAMPLE", percentage=30),
        fromStepId="label-1",
        toStepId="review-1",
    ),
    transition(
        "team-to-experts", 1, condition("ALWAYS"), fromStepGroupId="group-1", toStepId="label-2"
    ),
    transition(
        "into-review-2",
        1,
        condition("SAMPLE", percentage=100),
        fromStepId="label-2",
        toStepId="review-2",
    ),
    transition("experts-out", 1, condition("ALWAYS"), fromStepGroupId="group-2"),
]
# The stored transitions as the SDK sends them back: with their ids, without the null fields.
KEPT = {
    "into-review-1": {
        "id": "into-review-1",
        "fromStepId": "label-1",
        "toStepId": "review-1",
        "priority": 1,
        "condition": {"type": "SAMPLE", "percentage": 30},
    },
    "team-to-experts": {
        "id": "team-to-experts",
        "fromStepGroupId": "group-1",
        "toStepId": "label-2",
        "priority": 1,
        "condition": {"type": "ALWAYS"},
    },
    "into-review-2": {
        "id": "into-review-2",
        "fromStepId": "label-2",
        "toStepId": "review-2",
        "priority": 1,
        "condition": {"type": "SAMPLE", "percentage": 100},
    },
    "experts-out": {
        "id": "experts-out",
        "fromStepGroupId": "group-2",
        "priority": 1,
        "condition": {"type": "ALWAYS"},
    },
}
ANSWER = {"transitions": STORED, "warnings": ["A step was left last of its group."]}


@pytest.fixture()
def server() -> FakeWorkflowServer:
    return FakeWorkflowServer({**MULTI_GROUP_PROJECT, "workflowTransitions": STORED}, ANSWER)


def workflow_of(server: FakeWorkflowServer) -> WorkflowNamespace:
    return WorkflowNamespace(MagicMock(), gateway_of(server))


def sent_transitions(server: FakeWorkflowServer) -> list[dict]:
    name, sent = server.mutation
    assert name == "editProjectWorkflowSettings"
    return sent["transitions"]


def test_list_answers_the_stored_transitions(server):
    transitions = workflow_of(server).transitions.list(project_id="project")

    assert transitions == STORED
    assert "workflowTransitions{" in server.queries[0]


def test_create_sends_the_stored_transitions_with_their_ids_and_the_new_one(server):
    result = workflow_of(server).transitions.create(
        project_id="project",
        transitions=[
            {
                "from_step": {"name": "Labeling", "group_name": "Team"},
                "to_step": "Expert review",
                "priority": 2,
                "condition": {
                    "type": "CLASSIFICATION_INCLUDES",
                    "job_name": "QUALITY",
                    "categories": ["DOUBTFUL"],
                    "quantifier": "MORE_THAN",
                    "value": 2,
                },
            }
        ],
    )

    assert result["transitions"] == STORED
    assert result["warnings"] == ["A step was left last of its group."]
    assert sent_transitions(server) == [
        *KEPT.values(),
        {
            "fromStepId": "label-1",
            "toStepId": "review-2",
            "priority": 2,
            "condition": {
                "type": "CLASSIFICATION_INCLUDES",
                "jobName": "QUALITY",
                "categories": ["DOUBTFUL"],
                "quantifier": "MORE_THAN",
                "value": 2,
            },
        },
    ]
    assert "stepGroups" not in server.mutation[1]
    assert "warnings" in server.mutation_documents[0]
    assert "transitions{" in server.mutation_documents[0]


def test_create_from_the_end_of_a_group_out_of_the_workflow(server):
    workflow_of(server).transitions.create(
        project_id="project",
        transitions=[
            {"from_step_group": "Team", "priority": 2, "condition": {"type": "ALWAYS"}},
        ],
    )

    assert sent_transitions(server)[-1] == {
        "fromStepGroupId": "group-1",
        "priority": 2,
        "condition": {"type": "ALWAYS"},
    }


@pytest.mark.parametrize(
    "ends",
    [{}, {"from_step": "label-1", "from_step_group": "Team"}],
)
def test_create_needs_exactly_one_source(server, ends):
    with pytest.raises(ValueError, match="give exactly one"):
        workflow_of(server).transitions.create(
            project_id="project",
            transitions=[{**ends, "priority": 2, "condition": {"type": "ALWAYS"}}],
        )

    assert server.mutations == []


def test_update_changes_the_priority_and_condition_and_keeps_the_id(server):
    workflow_of(server).transitions.update(
        project_id="project",
        transitions=[
            {
                "id": "into-review-1",
                "to_step": "review-1",
                "condition": {"type": "SAMPLE", "percentage": 50},
            },
            {"id": "experts-out", "priority": 3, "to_step": None},
        ],
    )

    assert sent_transitions(server) == [
        {**KEPT["into-review-1"], "condition": {"type": "SAMPLE", "percentage": 50}},
        KEPT["team-to-experts"],
        KEPT["into-review-2"],
        {**KEPT["experts-out"], "priority": 3},
    ]


def test_update_refuses_another_target(server):
    with pytest.raises(ValueError, match="delete it and create another"):
        workflow_of(server).transitions.update(
            project_id="project",
            transitions=[{"id": "into-review-1", "to_step": "review-2", "priority": 2}],
        )

    assert server.mutations == []


def test_update_refuses_a_transition_the_project_does_not_have(server):
    with pytest.raises(ValueError, match="'missing' is not a transition of the project"):
        workflow_of(server).transitions.update(
            project_id="project", transitions=[{"id": "missing", "priority": 2}]
        )


def test_delete_sends_the_other_transitions(server):
    result = workflow_of(server).transitions.delete(
        project_id="project", transition_ids=["experts-out"]
    )

    assert result == ANSWER
    assert sent_transitions(server) == [
        KEPT["into-review-1"],
        KEPT["team-to-experts"],
        KEPT["into-review-2"],
    ]


def test_delete_refuses_a_transition_the_project_does_not_have(server):
    with pytest.raises(ValueError, match="'missing' is not a transition of the project"):
        workflow_of(server).transitions.delete(project_id="project", transition_ids=["missing"])


def test_a_transition_of_unreadable_condition_must_be_deleted_or_given_one():
    stored = [*STORED[:3], {**STORED[3], "condition": None}]
    server = FakeWorkflowServer({**MULTI_GROUP_PROJECT, "workflowTransitions": stored}, ANSWER)

    with pytest.raises(ValueError, match="'experts-out' has a condition the server can no longer"):
        workflow_of(server).transitions.update(
            project_id="project", transitions=[{"id": "into-review-1", "priority": 2}]
        )

    workflow_of(server).transitions.update(
        project_id="project",
        transitions=[{"id": "experts-out", "condition": {"type": "ALWAYS"}}],
    )
    assert sent_transitions(server)[-1] == KEPT["experts-out"]


def test_update_drops_the_transitions_of_a_step_it_deletes(server):
    workflow_of(server).update(
        project_id="project",
        delete_steps=["review-1"],
        delete_transitions=[],
    )

    _, sent = server.mutation
    assert sent["steps"]["deletes"] == ["review-1"]
    assert sent["transitions"] == [
        KEPT["team-to-experts"],
        KEPT["into-review-2"],
        KEPT["experts-out"],
    ]


def test_update_drops_the_transitions_of_a_group_it_deletes(server):
    workflow_of(server).update(
        project_id="project",
        delete_step_groups=["Experts"],
        create_transitions=[
            {"from_step_group": "Team", "priority": 1, "condition": {"type": "ALWAYS"}}
        ],
    )

    _, sent = server.mutation
    assert sent["stepGroups"]["deletes"] == ["group-2"]
    assert sent["transitions"] == [
        KEPT["into-review-1"],
        {"fromStepGroupId": "group-1", "priority": 1, "condition": {"type": "ALWAYS"}},
    ]


def test_update_refuses_a_transition_to_a_step_it_deletes(server):
    with pytest.raises(ValueError, match="Step 'review-1' not found"):
        workflow_of(server).update(
            project_id="project",
            delete_steps=["review-1"],
            create_transitions=[
                {
                    "from_step": "label-1",
                    "to_step": "review-1",
                    "priority": 1,
                    "condition": {"type": "ALWAYS"},
                }
            ],
        )


def test_update_names_the_steps_and_groups_it_creates_by_ids_it_gives_them(
    server, mocker: pytest_mock.MockerFixture
):
    mocker.patch(
        "kili.use_cases.project_workflow.transitions.cuid",
        side_effect=["audit", "audit-label", "audit-review"],
    )

    workflow_of(server).update(
        project_id="project",
        create_step_groups=[
            {
                "name": "Audit",
                "steps": [
                    {"type": "DEFAULT", "name": "Labeling", "assignees": ["labeler"]},
                    {"type": "REVIEW", "name": "Audit review", "assignees": ["reviewer"]},
                ],
            }
        ],
        create_transitions=[
            {
                "from_step_group": "Experts",
                "to_step": {"name": "Labeling", "group_name": "Audit"},
                "priority": 2,
                "condition": {"type": "ALWAYS"},
            },
            {
                "from_step": {"name": "Labeling", "group_name": "Audit"},
                "to_step": "Audit review",
                "priority": 1,
                "condition": {"type": "SAMPLE", "percentage": 10},
            },
            {"from_step_group": "audit", "priority": 1, "condition": {"type": "ALWAYS"}},
        ],
    )

    _, sent = server.mutation
    [group] = sent["stepGroups"]["creates"]
    assert group["id"] == "audit"
    assert [step["id"] for step in group["steps"]] == ["audit-label", "audit-review"]
    assert sent["transitions"][len(KEPT) :] == [
        {
            "fromStepGroupId": "group-2",
            "toStepId": "audit-label",
            "priority": 2,
            "condition": {"type": "ALWAYS"},
        },
        {
            "fromStepId": "audit-label",
            "toStepId": "audit-review",
            "priority": 1,
            "condition": {"type": "SAMPLE", "percentage": 10},
        },
        {"fromStepGroupId": "audit", "priority": 1, "condition": {"type": "ALWAYS"}},
    ]


def test_update_without_transition_list_sends_none(server):
    workflow_of(server).update(project_id="project", delete_steps=["review-1"])

    assert "transitions" not in server.mutation[1]


def test_saving_transitions_explains_a_server_that_predates_them(server):
    gateway = gateway_of(server)
    gateway.graphql_client.execute.side_effect = GraphQLError(
        'Cannot query field "workflowTransitions" on type "Project".'
    )

    with pytest.raises(GraphQLError, match="Saving the transitions needs a version of Kili"):
        WorkflowNamespace(MagicMock(), gateway).transitions.delete(
            project_id="project", transition_ids=["experts-out"]
        )


def test_a_transition_method_names_itself_by_its_path_in_the_log_context(server):
    workflow_of(server).transitions.list(project_id="project")

    assert LogContext()["kili-client-method-name"] == "projects.workflow.transitions.list"
