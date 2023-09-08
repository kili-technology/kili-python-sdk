"""Tests for issues use cases."""


import pytest_mock

from kili.adapters.kili_api_gateway import KiliAPIGateway
from kili.domain.issue import IssueId
from kili.use_cases.issue import IssueUseCases
from kili.use_cases.issue.types import IssueToCreateUseCaseInput


def test_create_one_issue(
    mocked_kili_api_gateway: KiliAPIGateway, mocker: pytest_mock.MockerFixture
):
    mocked_kili_api_gateway.create_issues.return_value = [IssueId("created_issue_id")]

    # given one issue to create
    issue = IssueToCreateUseCaseInput(label_id="label_id", text="text", object_mid="object_mid")

    # when creating one issue
    issues = IssueUseCases(mocked_kili_api_gateway).create_issues(
        project_id="project_id", issues=[issue]
    )

    # then
    assert issues == [IssueId("created_issue_id")]
