"""The step filters of the issue queries reach the API as step ids."""

import pytest
import pytest_mock

from kili.adapters.kili_api_gateway.issue.mappers import issue_where_mapper
from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.domain.issue import IssueFilters
from kili.domain.project import ProjectId
from kili.presentation.client.issue import IssueClientMethods

STEPS = (
    [
        {"id": "label", "name": "Label"},
        {"id": "internal-review", "name": "Internal review"},
        {"id": "client-review", "name": "Client review"},
    ],
    "V2",
)


@pytest.fixture()
def project_steps(mocker: pytest_mock.MockerFixture):
    return mocker.patch(
        "kili.presentation.client.issue.ProjectUseCases.get_project_steps_and_version",
        return_value=STEPS,
    )


@pytest.fixture()
def issues_client(mocker: pytest_mock.MockerFixture):
    kili = IssueClientMethods()
    kili.kili_api_gateway = mocker.MagicMock(spec=KiliAPIGateway)
    return kili


def test_issues_sends_the_ids_of_the_steps_named(
    issues_client, project_steps, mocker: pytest_mock.MockerFixture
):
    # Given a project whose steps include a client review
    list_issues = mocker.patch(
        "kili.presentation.client.issue.IssueUseCases.list_issues", return_value=iter([])
    )

    # When its issues are listed by step name
    issues_client.issues("project", step_name_in=["Client review"])

    # Then the step's id is sent
    project_steps.assert_called_once_with("project")
    assert list_issues.call_args.args[0].step_id_in == ["client-review"]


def test_count_issues_sends_the_step_ids_given_without_reading_the_steps(
    issues_client, project_steps, mocker: pytest_mock.MockerFixture
):
    count_issues = mocker.patch(
        "kili.presentation.client.issue.IssueUseCases.count_issues", return_value=0
    )

    issues_client.count_issues("project", step_id_in=["internal-review"])

    project_steps.assert_not_called()
    assert count_issues.call_args.args[0].step_id_in == ["internal-review"]


def test_count_issues_sends_no_step_filter_when_none_is_given(
    issues_client, project_steps, mocker: pytest_mock.MockerFixture
):
    count_issues = mocker.patch(
        "kili.presentation.client.issue.IssueUseCases.count_issues", return_value=0
    )

    issues_client.count_issues("project")

    project_steps.assert_not_called()
    assert count_issues.call_args.args[0].step_id_in is None


def test_issues_refuses_a_step_filter_given_by_id_and_by_name(issues_client, project_steps):
    with pytest.raises(ValueError, match="both given"):
        issues_client.issues("project", step_id_in=["label"], step_name_in=["Label"])


def test_issues_refuses_a_step_name_the_project_does_not_have(issues_client, project_steps):
    with pytest.raises(ValueError, match="do not match any steps"):
        issues_client.issues("project", step_name_in=["Review 3"])


def test_issue_where_mapper_sends_the_step_ids():
    where = issue_where_mapper(
        IssueFilters(project_id=ProjectId("project"), step_id_in=["client-review"])
    )

    assert where["stepIdIn"] == ["client-review"]
