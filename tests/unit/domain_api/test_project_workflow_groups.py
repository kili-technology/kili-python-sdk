"""Tests for kili.projects.workflow.groups."""

from unittest.mock import MagicMock

import pytest
import pytest_mock

from kili.domain_api.project_workflow import WorkflowNamespace
from kili.utils.logcontext import LogContext
from tests.unit.domain_api.project_workflow_fakes import (
    MULTI_GROUP_PROJECT,
    MULTI_STEP_PROJECT,
    FakeWorkflowServer,
    gateway_of,
)

NEW_GROUP = {
    "id": "group-new",
    "name": "Audit",
    "order": 3,
    "allowedJobNames": ["CLASSIFICATION"],
    "steps": [
        {"id": "label-new", "name": "Audit labeling", "type": "DEFAULT"},
        {"id": "review-new", "name": "Audit review", "type": "REVIEW"},
    ],
}


@pytest.fixture()
def new_ids(mocker: pytest_mock.MockerFixture):
    return mocker.patch(
        "kili.use_cases.project_workflow.step_groups.cuid",
        side_effect=["group-new", "label-new", "review-new"],
    )


def groups_of(server: FakeWorkflowServer):
    return WorkflowNamespace(MagicMock(), gateway_of(server)).groups


def test_list_answers_the_groups_with_their_steps():
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT)

    groups = groups_of(server).list(project_id="project")

    assert [group["name"] for group in groups] == ["Team", "Experts"]
    assert "stepGroups{" in server.queries[0]
    assert "allowedJobNames" in server.queries[0]


@pytest.mark.usefixtures("new_ids")
def test_create_sends_the_group_with_its_labeling_step_and_its_review():
    server = FakeWorkflowServer(
        MULTI_GROUP_PROJECT, answer={"stepGroups": [*MULTI_GROUP_PROJECT["stepGroups"], NEW_GROUP]}
    )

    group = groups_of(server).create(
        project_id="project",
        name="Audit",
        labeling_step_name="Audit labeling",
        labelers=["labeler@acme.com", "reviewer@acme.com"],
        review_step_name="Audit review",
        reviewers=["reviewer@acme.com"],
        sample_percentage=30,
        allowed_job_names=["CLASSIFICATION"],
    )

    assert group == NEW_GROUP
    name, sent = server.mutation
    assert name == "editProjectWorkflowSettings"
    assert sent["stepGroups"] == {
        "creates": [
            {
                "id": "group-new",
                "name": "Audit",
                "allowedJobNames": ["CLASSIFICATION"],
                "steps": [
                    {
                        "id": "label-new",
                        "name": "Audit labeling",
                        "type": "DEFAULT",
                        "assignees": ["labeler", "reviewer"],
                    },
                    {
                        "id": "review-new",
                        "name": "Audit review",
                        "type": "REVIEW",
                        "assignees": ["reviewer"],
                        "stepCoverage": 30,
                    },
                ],
            }
        ],
        "updates": [],
        "deletes": [],
    }
    assert sent["steps"] == {"creates": [], "updates": [], "deletes": []}


@pytest.mark.usefixtures("new_ids")
def test_create_refuses_a_review_left_with_labelers_only():
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT)

    with pytest.warns(UserWarning, match="not found or can not review"), pytest.raises(
        ValueError, match="who is not a labeler"
    ):
        groups_of(server).create(
            project_id="project",
            name="Audit",
            labeling_step_name="Audit labeling",
            labelers=["labeler@acme.com"],
            review_step_name="Audit review",
            reviewers=["labeler@acme.com"],
            sample_percentage=30,
        )

    assert server.mutations == []


def test_create_refuses_a_sample_percentage_over_100():
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT)

    with pytest.raises(ValueError, match="sample_percentage must be between 0 and 100"):
        groups_of(server).create(
            project_id="project",
            name="Audit",
            labeling_step_name="Audit labeling",
            labelers=["labeler@acme.com"],
            review_step_name="Audit review",
            reviewers=["reviewer@acme.com"],
            sample_percentage=101,
        )


@pytest.mark.parametrize("group", ["Experts", "group-2"])
def test_update_sends_the_group_by_id_whether_given_by_name_or_id(group):
    renamed = {**MULTI_GROUP_PROJECT["stepGroups"][1], "name": "Senior experts"}
    server = FakeWorkflowServer(
        MULTI_GROUP_PROJECT, answer={"stepGroups": [MULTI_GROUP_PROJECT["stepGroups"][0], renamed]}
    )

    updated = groups_of(server).update(project_id="project", group=group, name="Senior experts")

    assert updated == renamed
    assert server.mutation[1]["stepGroups"] == {
        "creates": [],
        "updates": [{"id": "group-2", "name": "Senior experts"}],
        "deletes": [],
    }


def test_update_sends_the_allowed_job_names():
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT, answer=MULTI_GROUP_PROJECT)

    groups_of(server).update(project_id="project", group="Team", allowed_job_names=[])

    assert server.mutation[1]["stepGroups"]["updates"] == [{"id": "group-1", "allowedJobNames": []}]


def test_update_refuses_a_call_that_changes_nothing():
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT)

    with pytest.raises(ValueError, match="new name of the group, or its allowed job names"):
        groups_of(server).update(project_id="project", group="Team")


@pytest.mark.parametrize("group", ["Experts", "group-2"])
def test_delete_sends_the_group_by_id(group):
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT, answer=MULTI_GROUP_PROJECT)

    deleted = groups_of(server).delete(project_id="project", group=group)

    assert deleted == {"id": "group-2"}
    assert server.mutation[1]["stepGroups"] == {
        "creates": [],
        "updates": [],
        "deletes": ["group-2"],
    }


def test_a_group_name_unknown_to_the_project_is_refused():
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT)

    with pytest.raises(ValueError, match="Group 'Missing' not found"):
        groups_of(server).delete(project_id="project", group="Missing")


def test_groups_are_refused_outside_the_multi_group_workflow():
    server = FakeWorkflowServer(MULTI_STEP_PROJECT)

    with pytest.raises(ValueError, match="only available in the multi-group workflow"):
        groups_of(server).delete(project_id="project", group="default")

    assert server.mutations == []


def test_a_group_method_names_itself_by_its_path_in_the_log_context():
    server = FakeWorkflowServer(MULTI_GROUP_PROJECT)

    groups_of(server).list(project_id="project")

    assert LogContext()["kili-client-method-name"] == "projects.workflow.groups.list"
