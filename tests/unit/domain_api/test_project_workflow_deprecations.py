"""The workflow methods replaced by kili.projects.workflow.steps warn, and keep working."""

from unittest.mock import MagicMock

import pytest

from kili.domain_api.project_workflow import WORKFLOW_LIST_DEPRECATION, WorkflowNamespace
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
