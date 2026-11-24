"""Each workflow method of the client names itself in the log context its requests carry."""

import pytest
import pytest_mock

from kili.presentation.client.project_workflow import ProjectWorkflowClientMethods
from kili.utils.logcontext import LogContext


@pytest.fixture()
def kili(mocker: pytest_mock.MockerFixture):
    client = ProjectWorkflowClientMethods()
    client.kili_api_gateway = mocker.MagicMock()
    return client


def test_get_steps_names_itself_in_the_log_context(kili):
    kili.kili_api_gateway.get_steps.return_value = [{"id": "step-1", "name": "Labeling"}]

    kili.get_steps(project_id="project")

    assert LogContext()["kili-client-method-name"] == "get_steps"


def test_rename_step_names_itself_in_the_log_context(kili):
    kili.kili_api_gateway.get_step.return_value = {"id": "step-1"}
    kili.kili_api_gateway.rename_step.return_value = {"id": "step-1", "name": "Review"}

    kili.rename_step(project_id="project", step_id="step-1", new_name="Review")

    assert LogContext()["kili-client-method-name"] == "rename_step"
