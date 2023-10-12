"""Tests for issues use cases."""


from typing import Generator

import pytest_mock

from kili.adapters.kili_api_gateway import KiliAPIGateway
from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.domain.issue import IssueFilters, IssueId
from kili.domain.project import ProjectId
from kili.use_cases.issue import IssueUseCases
from kili.use_cases.issue.types import IssueToCreateUseCaseInput


def test_create_one_issue(kili_api_gateway: KiliAPIGateway, mocker: pytest_mock.MockerFixture):
    mocker.patch(
        "kili.use_cases.issue.get_labels_asset_ids_map", return_value={"label_id": "asset_id"}
    )
    kili_api_gateway.create_issues.return_value = [IssueId("created_issue_id")]

    # given one issue to create
    issue = IssueToCreateUseCaseInput(label_id="label_id", text="text", object_mid="object_mid")

    # when creating one issue
    issues = IssueUseCases(kili_api_gateway).create_issues(project_id="project_id", issues=[issue])

    # then
    assert issues == [IssueId("created_issue_id")]


def test_count_issues(kili_api_gateway: KiliAPIGateway):
    # Given
    kili_api_gateway.count_issues.return_value = 42

    # When
    nb_issues = IssueUseCases(kili_api_gateway).count_issues(
        IssueFilters(project_id=ProjectId("fake_proj_id"))
    )

    # Then
    assert nb_issues == 42


def test_list_issues(kili_api_gateway: KiliAPIGateway):
    # Given
    kili_api_gateway.list_issues.return_value = (issue for issue in [{"id": "123"}, {"id": "456"}])

    # When
    issues = IssueUseCases(kili_api_gateway).list_issues(
        options=QueryOptions(disable_tqdm=True),
        filters=IssueFilters(project_id=ProjectId("fake_proj_id")),
        fields=("id",),
    )

    # Then
    assert isinstance(issues, Generator)
    assert list(issues) == [{"id": "123"}, {"id": "456"}]
