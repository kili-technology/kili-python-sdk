"""Tests for the send_back_to_previous_step of kili.projects.workflow.steps."""

from unittest.mock import MagicMock

import pytest

from kili.domain_api.project_workflow import WorkflowNamespace
from kili.exceptions import GraphQLError
from tests.unit.domain_api.project_workflow_fakes import (
    MULTI_GROUP_PROJECT,
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


def steps_of(server: FakeWorkflowServer):
    return WorkflowNamespace(MagicMock(), gateway_of(server)).steps


def test_create_sends_a_review_back_to_the_previous_step():
    server = FakeWorkflowServer(
        MULTI_GROUP_PROJECT, answer={"steps": [*MULTI_GROUP_PROJECT["steps"], NEW_REVIEW]}
    )

    steps_of(server).create(
        project_id="project",
        name="Second review",
        assignees=["reviewer@acme.com"],
        group_name="Experts",
        sample_percentage=20,
        send_back_to_previous_step=True,
    )

    name, sent = server.mutation
    assert name == "addReviewStep"
    assert sent["sendBackToPreviousStep"] is True
    assert "sendBackStepId" not in sent


def test_update_sends_a_review_back_to_the_previous_step():
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT, answer=MULTI_GROUP_PROJECT)

    steps_of(server).update(project_id="project", step="review-2", send_back_to_previous_step=True)

    assert server.mutation[1]["steps"]["updates"] == [
        {"id": "review-2", "sendBackToPreviousStep": True}
    ]


def test_update_turns_it_off_while_naming_a_step():
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT, answer=MULTI_GROUP_PROJECT)

    steps_of(server).update(
        project_id="project",
        step="review-2",
        send_back_to_step="label-2",
        send_back_to_previous_step=False,
    )

    assert server.mutation[1]["steps"]["updates"] == [
        {"id": "review-2", "sendBackStepId": "label-2", "sendBackToPreviousStep": False}
    ]


def test_a_review_sends_back_to_a_step_or_to_the_previous_one_not_both():
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT)

    with pytest.raises(ValueError, match="not both"):
        steps_of(server).update(
            project_id="project",
            step="review-2",
            send_back_to_step="label-2",
            send_back_to_previous_step=True,
        )

    assert server.mutations == []


def test_a_labeling_step_does_not_send_back():
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT)

    with pytest.raises(ValueError, match="send_back_to_previous_step is set on a review"):
        steps_of(server).update(
            project_id="project", step="label-1", send_back_to_previous_step=False
        )


def test_a_server_that_predates_it_is_explained():
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT)
    gateway = gateway_of(server)

    def refuse_the_mutation(query, variables=None, **kwargs):
        if query.lstrip().startswith("mutation"):
            raise GraphQLError(
                'Field "sendBackToPreviousStep" is not defined by type "UpdateProjectWorkflowStepInput".'
            )
        return server.execute(query, variables, **kwargs)

    gateway.graphql_client.execute.side_effect = refuse_the_mutation

    with pytest.raises(GraphQLError, match="send_back_to_previous_step needs a version of Kili"):
        WorkflowNamespace(MagicMock(), gateway).steps.update(
            project_id="project", step="review-2", send_back_to_previous_step=True
        )
