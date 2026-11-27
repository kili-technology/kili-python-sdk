"""The deprecated workflow methods and keys warn, and keep working."""

import warnings
from unittest.mock import MagicMock

import pytest

from kili.domain_api.project_workflow import (
    STEP_COVERAGE_DEPRECATION,
    WORKFLOW_LIST_DEPRECATION,
    WorkflowNamespace,
)
from kili.presentation.client.project_workflow import (
    DELETE_LAST_STEP_DEPRECATION,
    ProjectWorkflowClientMethods,
)


def test_workflow_list_warns_and_answers_the_steps():
    client = MagicMock()
    client.get_steps.return_value = [{"id": "label", "name": "Labeling"}]

    with pytest.warns(DeprecationWarning) as records:
        steps = WorkflowNamespace(client, MagicMock()).list(project_id="project")

    assert [str(record.message) for record in records] == [WORKFLOW_LIST_DEPRECATION]
    assert steps == [{"id": "label", "name": "Labeling"}]
    client.get_steps.assert_called_once_with(project_id="project")


def test_delete_last_step_warns_and_deletes_the_last_step():
    kili = ProjectWorkflowClientMethods()
    kili.kili_api_gateway = MagicMock()
    kili.kili_api_gateway.get_steps.return_value = [
        {"id": "label", "name": "Labeling"},
        {"id": "review", "name": "Review"},
        {"id": "second-review", "name": "Second review"},
    ]
    kili.kili_api_gateway.delete_step.return_value = {"steps": [{"id": "label"}, {"id": "review"}]}

    with pytest.warns(DeprecationWarning) as records:
        result = kili.delete_last_step(project_id="project")

    assert [str(record.message) for record in records] == [DELETE_LAST_STEP_DEPRECATION]
    assert result == {"steps": [{"id": "label"}, {"id": "review"}]}
    deleted = kili.kili_api_gateway.delete_step.call_args.args[0]
    assert (deleted.project_id, deleted.step_id) == ("project", "second-review")


@pytest.mark.parametrize(
    "steps",
    [
        {"create_steps": [{"type": "REVIEW", "name": "R", "assignees": ["u"], "step_coverage": 5}]},
        {"update_steps": [{"id": "review", "step_coverage": 5}]},
        {
            "create_step_groups": [
                {
                    "name": "Audit",
                    "steps": [
                        {"type": "DEFAULT", "name": "L", "assignees": ["u"]},
                        {"type": "REVIEW", "name": "R", "assignees": ["u"], "step_coverage": 5},
                    ],
                }
            ]
        },
    ],
)
def test_workflow_update_warns_of_a_step_coverage_and_sends_it(steps):
    gateway = MagicMock()
    gateway.update_project_workflow.return_value = {"steps": []}

    with pytest.warns(DeprecationWarning) as records:
        WorkflowNamespace(MagicMock(), gateway).update(project_id="project", **steps)

    assert [str(record.message) for record in records] == [STEP_COVERAGE_DEPRECATION]
    gateway.update_project_workflow.assert_called_once()


def test_workflow_update_without_step_coverage_does_not_warn():
    gateway = MagicMock()
    gateway.update_project_workflow.return_value = {"steps": []}

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        WorkflowNamespace(MagicMock(), gateway).update(
            project_id="project",
            create_steps=[{"type": "REVIEW", "name": "R", "assignees": ["u"]}],
        )
