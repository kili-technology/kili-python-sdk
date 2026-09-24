"""Tests for issues use cases."""

from collections.abc import Generator
from unittest.mock import call

import pytest
import pytest_mock

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.domain.issue import IssueFilters, IssueId
from kili.domain.label import LabelId
from kili.domain.project import ProjectId
from kili.exceptions import GraphQLError
from kili.use_cases.issue import IssueUseCases
from kili.use_cases.issue.types import IssueToCreateUseCaseInput


def test_create_one_issue(kili_api_gateway: KiliAPIGateway, mocker: pytest_mock.MockerFixture):
    kili_api_gateway.create_issues.return_value = [IssueId("created_issue_id")]

    # given one issue to create
    issue = IssueToCreateUseCaseInput(
        label_id=LabelId("label_id"), text="text", object_mid="object_mid"
    )

    # when creating one issue
    issues = IssueUseCases(kili_api_gateway).create_issues(
        project_id=ProjectId("project_id"), issues=[issue]
    )

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


def _comment(issue_id: str, text: str) -> dict:
    return {"id": f"comment_{issue_id}", "issueId": issue_id, "text": text}


def test_reply_to_issues_adds_one_comment_per_issue_in_order(kili_api_gateway: KiliAPIGateway):
    # Given
    kili_api_gateway.append_to_comments.side_effect = lambda issue_id, text: _comment(
        issue_id, text
    )

    # When
    comments = IssueUseCases(kili_api_gateway).reply_to_issues(
        issue_ids=[IssueId("issue_1"), IssueId("question_2")],
        texts=["Fixed", "It is a cat"],
        disable_tqdm=True,
    )

    # Then
    assert comments == [_comment("issue_1", "Fixed"), _comment("question_2", "It is a cat")]
    assert kili_api_gateway.append_to_comments.call_args_list == [
        call(issue_id="issue_1", text="Fixed"),
        call(issue_id="question_2", text="It is a cat"),
    ]


def test_reply_to_issues_refuses_an_empty_text_before_any_call(kili_api_gateway: KiliAPIGateway):
    # When / Then
    with pytest.raises(ValueError, match="cannot be empty"):
        IssueUseCases(kili_api_gateway).reply_to_issues(
            issue_ids=[IssueId("issue_1"), IssueId("issue_2")],
            texts=["Fixed", "   "],
            disable_tqdm=True,
        )
    kili_api_gateway.append_to_comments.assert_not_called()


def test_reply_to_issues_names_the_failing_issue_and_the_ones_already_replied_to(
    kili_api_gateway: KiliAPIGateway,
):
    # Given the second issue belongs to a project the user is not a member of
    access_denied = GraphQLError(
        error=[{"message": "[accessDenied] Access denied."}], context={"foo": "bar"}
    )
    kili_api_gateway.append_to_comments.side_effect = [
        _comment("issue_1", "Fixed"),
        access_denied,
        _comment("issue_3", "Fixed"),
    ]

    # When
    with pytest.raises(GraphQLError) as raised:
        IssueUseCases(kili_api_gateway).reply_to_issues(
            issue_ids=[IssueId("issue_1"), IssueId("issue_2"), IssueId("issue_3")],
            texts=["Fixed", "Fixed", "Fixed"],
            disable_tqdm=True,
        )

    # Then it stops at the failing issue
    message = str(raised.value)
    assert message == (
        'GraphQL error: "Could not reply to issue issue_2, no comment was added to it (issues'
        " already replied to in this call: ['issue_1']): [accessDenied] Access denied.\""
    )
    assert raised.value.error == [{"message": "[accessDenied] Access denied."}]
    assert raised.value.context == {"foo": "bar"}
    assert raised.value.__cause__ is access_denied
    assert kili_api_gateway.append_to_comments.call_count == 2
