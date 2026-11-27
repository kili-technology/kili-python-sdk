"""Tests for kili.projects.workflow.update."""

from unittest.mock import MagicMock

import pytest

from kili.domain_api.project_workflow import WorkflowNamespace
from kili.utils.logcontext import LogContext
from tests.unit.domain_api.project_workflow_fakes import (
    MULTI_GROUP_PROJECT,
    MULTI_STEP_PROJECT,
    FakeWorkflowServer,
    gateway_of,
)

ANSWER = {"enforceStepSeparation": True, "steps": [], "stepGroups": []}


def workflow_of(server: FakeWorkflowServer) -> WorkflowNamespace:
    return WorkflowNamespace(MagicMock(), gateway_of(server))


def test_update_creates_a_group_and_a_step_in_it_named_by_their_client_ids():
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT, answer=ANSWER)

    result = workflow_of(server).update(
        project_id="project",
        create_step_groups=[
            {
                "id": "group-audit",
                "name": "Audit",
                "allowed_job_names": ["CLASSIFICATION"],
                "steps": [
                    {"id": "audit-label", "type": "DEFAULT", "name": "Label", "assignees": ["u1"]},
                    {
                        "id": "audit-review",
                        "type": "REVIEW",
                        "name": "Review",
                        "assignees": ["u2"],
                        "step_coverage": 100,
                    },
                ],
            }
        ],
        create_steps=[
            {
                "id": "audit-second-review",
                "type": "REVIEW",
                "name": "Second review",
                "assignees": ["u2"],
                "step_group_id": "group-audit",
                "send_back_step_id": "audit-label",
            }
        ],
    )

    assert result == ANSWER
    name, sent = server.mutation
    assert name == "editProjectWorkflowSettings"
    assert sent["projectId"] == "project"
    assert sent["stepGroups"]["creates"] == [
        {
            "id": "group-audit",
            "name": "Audit",
            "allowedJobNames": ["CLASSIFICATION"],
            "steps": [
                {"id": "audit-label", "type": "DEFAULT", "name": "Label", "assignees": ["u1"]},
                {
                    "id": "audit-review",
                    "type": "REVIEW",
                    "name": "Review",
                    "assignees": ["u2"],
                    "stepCoverage": 100,
                },
            ],
        }
    ]
    assert sent["steps"]["creates"] == [
        {
            "id": "audit-second-review",
            "type": "REVIEW",
            "name": "Second review",
            "assignees": ["u2"],
            "stepGroupId": "group-audit",
            "sendBackStepId": "audit-label",
        }
    ]


def test_update_sends_the_groups_to_update_and_to_delete_by_id():
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT, answer=ANSWER)

    workflow_of(server).update(
        project_id="project",
        update_step_groups=[{"id": "group-1", "name": "Juniors"}],
        delete_step_groups=["Experts"],
    )

    assert server.mutation[1]["stepGroups"] == {
        "creates": [],
        "updates": [{"id": "group-1", "name": "Juniors"}],
        "deletes": ["group-2"],
    }


def test_update_without_group_change_sends_no_step_groups():
    server = FakeWorkflowServer(MULTI_STEP_PROJECT, answer=ANSWER)

    workflow_of(server).update(
        project_id="project",
        enforce_step_separation=False,
        create_steps=[{"type": "REVIEW", "name": "Second review", "assignees": ["u2"]}],
    )

    sent = server.mutation[1]
    assert "stepGroups" not in sent
    assert sent["enforceStepSeparation"] is False
    assert sent["steps"]["creates"] == [
        {"type": "REVIEW", "name": "Second review", "assignees": ["u2"]}
    ]


def test_update_keeps_an_asset_s_path_after_a_send_back_when_asked():
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT, answer=ANSWER)

    workflow_of(server).update(project_id="project", keep_path_after_send_back=True)

    assert server.mutation[1]["keepPathAfterSendBack"] is True


def test_update_sends_no_path_setting_when_not_given():
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT, answer=ANSWER)

    workflow_of(server).update(project_id="project", enforce_step_separation=False)

    assert "keepPathAfterSendBack" not in server.mutation[1]


def test_update_refuses_a_step_of_a_new_group_given_a_group():
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT, answer=ANSWER)

    with pytest.raises(ValueError, match="take no step_group_id"):
        workflow_of(server).update(
            project_id="project",
            create_step_groups=[
                {
                    "name": "Audit",
                    "steps": [
                        {
                            "type": "DEFAULT",
                            "name": "Label",
                            "assignees": ["u1"],
                            "step_group_id": "group-1",
                        }
                    ],
                }
            ],
        )

    assert server.mutations == []


def test_update_names_itself_by_its_path_in_the_log_context():
    server = FakeWorkflowServer(MULTI_STEP_PROJECT, answer=ANSWER)

    workflow_of(server).update(project_id="project", enforce_step_separation=True)

    assert LogContext()["kili-client-method-name"] == "projects.workflow.update"
