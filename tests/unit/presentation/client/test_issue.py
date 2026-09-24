import pytest
import pytest_mock

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.domain.issue import IssueId
from kili.presentation.client.issue import IssueClientMethods


def test_given_issue_ids_and_texts_when_calling_reply_to_issues_it_replies_to_each_issue(
    mocker: pytest_mock.MockerFixture, kili_api_gateway: KiliAPIGateway
):
    # Given
    kili = IssueClientMethods()
    kili.kili_api_gateway = kili_api_gateway
    created_comments = [{"id": "comment_1"}, {"id": "comment_2"}]
    mock_reply_to_issues = mocker.patch(
        "kili.presentation.client.issue.IssueUseCases.reply_to_issues",
        return_value=created_comments,
    )

    # When
    comments = kili.reply_to_issues(
        issue_ids=["issue_1", "question_2"],
        text_array=["Fixed", "It is a cat"],
        disable_tqdm=True,
    )

    # Then
    assert comments == created_comments
    mock_reply_to_issues.assert_called_once_with(
        issue_ids=[IssueId("issue_1"), IssueId("question_2")],
        texts=["Fixed", "It is a cat"],
        disable_tqdm=True,
    )


def test_given_arrays_of_different_sizes_when_calling_reply_to_issues_it_raises(
    kili_api_gateway: KiliAPIGateway,
):
    # Given
    kili = IssueClientMethods()
    kili.kili_api_gateway = kili_api_gateway

    # When / Then
    with pytest.raises(ValueError, match="same length"):
        kili.reply_to_issues(issue_ids=["issue_1", "issue_2"], text_array=["Fixed"])
    kili_api_gateway.append_to_comments.assert_not_called()
