"""Tests for kili.projects.workflow.get."""

from unittest.mock import MagicMock

import pytest

from kili.domain_api.project_workflow import WorkflowNamespace
from kili.exceptions import GraphQLError
from tests.unit.domain_api.project_workflow_fakes import (
    MULTI_GROUP_PROJECT,
    FakeWorkflowServer,
    gateway_of,
)

TRANSITION = {
    "id": "transition-1",
    "fromStepId": "label-1",
    "fromStepGroupId": None,
    "toStepId": "review-1",
    "priority": 1,
    "condition": {
        "type": "SAMPLE",
        "percentage": 30,
        "jobName": None,
        "categories": None,
        "quantifier": None,
        "value": None,
    },
}


def workflow_of(server: FakeWorkflowServer) -> WorkflowNamespace:
    return WorkflowNamespace(MagicMock(), gateway_of(server))


def test_get_answers_the_steps_groups_and_transitions_in_one_query():
    project = {
        **MULTI_GROUP_PROJECT,
        "workflowTransitions": [TRANSITION],
        "usesConditionalRouting": False,
        "canEditTransitions": True,
        "enforceStepSeparation": True,
    }
    server = FakeWorkflowServer(project)

    workflow = workflow_of(server).get(project_id="project")

    assert workflow == project
    [query] = server.queries
    for field in (
        "usesConditionalRouting",
        "canEditTransitions",
        "enforceStepSeparation",
        "sendBackToPreviousStep",
        "workflowTransitions{",
        "condition{",
        "quantifier",
    ):
        assert field in query


def test_get_explains_a_server_that_predates_the_conditional_routing_workflow():
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT)
    gateway = gateway_of(server)
    gateway.graphql_client.execute.side_effect = GraphQLError(
        'Cannot query field "workflowTransitions" on type "Project".'
    )

    with pytest.raises(
        GraphQLError,
        match=r"kili.projects.workflow.get\(\) needs a version of Kili that serves the"
        r" conditional routing workflow \(LAB-4823\)",
    ):
        WorkflowNamespace(MagicMock(), gateway).get(project_id="project")


def test_get_lets_any_other_error_through():
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT)
    gateway = gateway_of(server)
    gateway.graphql_client.execute.side_effect = GraphQLError("Not authorized")

    with pytest.raises(GraphQLError, match="Not authorized") as raised:
        WorkflowNamespace(MagicMock(), gateway).get(project_id="project")

    assert "conditional routing" not in str(raised.value)
