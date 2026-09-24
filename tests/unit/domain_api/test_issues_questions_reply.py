"""Unit tests for the reply method of the issues and questions domain namespaces."""

from unittest.mock import MagicMock

import pytest
import pytest_mock

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.client import Kili
from kili.domain.issue import IssueId
from kili.domain_api.issues import IssuesNamespace
from kili.domain_api.questions import QuestionsNamespace


@pytest.fixture()
def mock_client():
    client = MagicMock(spec=Kili)
    client.disable_tqdm = True
    return client


@pytest.fixture()
def mock_gateway():
    return MagicMock(spec=KiliAPIGateway)


@pytest.fixture()
def mock_reply_to_issues(mocker: pytest_mock.MockerFixture):
    return mocker.patch(
        "kili.use_cases.issue.IssueUseCases.reply_to_issues",
        return_value=[{"id": "comment_1"}],
    )


class TestIssuesReply:
    def test_reply_to_one_issue(self, mock_client, mock_gateway, mock_reply_to_issues):
        issues = IssuesNamespace(mock_client, mock_gateway)

        comments = issues.reply(issue_id="issue_1", text="Fixed")

        assert comments == [{"id": "comment_1"}]
        mock_reply_to_issues.assert_called_once_with(
            issue_ids=[IssueId("issue_1")], texts=["Fixed"], disable_tqdm=True
        )

    def test_reply_to_several_issues(self, mock_client, mock_gateway, mock_reply_to_issues):
        issues = IssuesNamespace(mock_client, mock_gateway)

        issues.reply(
            issue_ids=["issue_1", "issue_2"],
            text_array=["Fixed", "Not an error"],
            disable_tqdm=False,
        )

        mock_reply_to_issues.assert_called_once_with(
            issue_ids=[IssueId("issue_1"), IssueId("issue_2")],
            texts=["Fixed", "Not an error"],
            disable_tqdm=False,
        )

    def test_reply_with_arrays_of_different_sizes_raises(
        self, mock_client, mock_gateway, mock_reply_to_issues
    ):
        issues = IssuesNamespace(mock_client, mock_gateway)

        with pytest.raises(ValueError, match="same length"):
            issues.reply(issue_ids=["issue_1", "issue_2"], text_array=["Fixed"])
        mock_reply_to_issues.assert_not_called()


class TestQuestionsReply:
    def test_reply_to_one_question(self, mock_client, mock_gateway, mock_reply_to_issues):
        questions = QuestionsNamespace(mock_client, mock_gateway)

        comments = questions.reply(question_id="question_1", text="It is a cat")

        assert comments == [{"id": "comment_1"}]
        mock_reply_to_issues.assert_called_once_with(
            issue_ids=[IssueId("question_1")], texts=["It is a cat"], disable_tqdm=True
        )

    def test_reply_to_several_questions(self, mock_client, mock_gateway, mock_reply_to_issues):
        questions = QuestionsNamespace(mock_client, mock_gateway)

        questions.reply(question_ids=["question_1", "question_2"], text_array=["Yes", "No"])

        mock_reply_to_issues.assert_called_once_with(
            issue_ids=[IssueId("question_1"), IssueId("question_2")],
            texts=["Yes", "No"],
            disable_tqdm=True,
        )

    def test_reply_without_text_raises(self, mock_client, mock_gateway, mock_reply_to_issues):
        questions = QuestionsNamespace(mock_client, mock_gateway)

        with pytest.raises(AssertionError, match="text_array must be provided"):
            questions.reply(question_id="question_1")  # pyright: ignore[reportCallIssue]
        mock_reply_to_issues.assert_not_called()
