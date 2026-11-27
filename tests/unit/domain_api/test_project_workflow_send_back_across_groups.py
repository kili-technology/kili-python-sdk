"""A review sends back to the labeling step of a group leading to its own, given as any step."""

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

# "Team" leads to "Experts": the labeling step of "Team" is a send back target of "Expert review".
TEAM_LABELING = {"name": "Labeling", "group_name": "Team"}
REFUSAL = (
    'Cannot send back to step "Team · Labeling": no path of transitions leads from it to'
    ' "Experts · Expert review"'
)


def steps_of(server: FakeWorkflowServer):
    return WorkflowNamespace(MagicMock(), gateway_of(server)).steps


@pytest.mark.parametrize("target", [TEAM_LABELING, "label-1"])
def test_update_sends_back_to_the_labeling_step_of_another_group(target):
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT, answer=MULTI_GROUP_PROJECT)

    steps_of(server).update(
        project_id="project",
        step={"name": "Expert review", "group_name": "Experts"},
        send_back_to_step=target,
    )

    assert server.mutation[1]["steps"]["updates"] == [
        {"id": "review-2", "sendBackStepId": "label-1"}
    ]


def test_create_sends_back_to_the_labeling_step_of_another_group():
    new_review = {
        "id": "review-new",
        "name": "Audit review",
        "type": "REVIEW",
        "stepGroupId": "group-2",
        "assignees": assignees("reviewer"),
    }
    server = FakeWorkflowServer(
        MULTI_GROUP_PROJECT, answer={"steps": [*MULTI_GROUP_PROJECT["steps"], new_review]}
    )

    steps_of(server).create(
        project_id="project",
        name="Audit review",
        assignees=["reviewer@acme.com"],
        group_name="Experts",
        sample_percentage=10,
        send_back_to_step=TEAM_LABELING,
    )

    assert server.mutation == (
        "addReviewStep",
        {
            "projectId": "project",
            "name": "Audit review",
            "assignees": ["reviewer"],
            "stepCoverage": 10,
            "sendBackStepId": "label-1",
            "stepGroupId": "group-2",
        },
    )


def test_the_server_decides_which_targets_it_accepts():
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT)
    gateway = gateway_of(server)

    def refuse_the_mutation(query, variables=None, **kwargs):
        if query.lstrip().startswith("mutation"):
            raise GraphQLError(REFUSAL)
        return server.execute(query, variables, **kwargs)

    gateway.graphql_client.execute.side_effect = refuse_the_mutation

    with pytest.raises(GraphQLError) as refused:
        WorkflowNamespace(MagicMock(), gateway).steps.update(
            project_id="project", step="review-2", send_back_to_step=TEAM_LABELING
        )

    assert str(refused.value) == f'GraphQL error: "{REFUSAL}"'
