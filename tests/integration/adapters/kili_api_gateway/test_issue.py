from kili.adapters.http_client import HttpClient
from kili.adapters.kili_api_gateway.issue.operations import GQL_APPEND_TO_COMMENTS
from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.core.graphql.graphql_client import GraphQLClient
from kili.domain.issue import IssueId


def test_given_kili_gateway_when_appending_to_comments_it_calls_proper_resolver(
    graphql_client: GraphQLClient, http_client: HttpClient
):
    # Given
    created_comment = {
        "id": "comment_id",
        "issueId": "issue_id",
        "text": "Fixed, thanks",
        "createdAt": "2026-09-24T12:00:00.000Z",
        "authorIdUser": "user_id",
    }
    graphql_client.execute.return_value = {"data": created_comment}
    kili_gateway = KiliAPIGateway(graphql_client=graphql_client, http_client=http_client)

    # When
    comment = kili_gateway.append_to_comments(issue_id=IssueId("issue_id"), text="Fixed, thanks")

    # Then
    assert comment == created_comment
    graphql_client.execute.assert_called_once_with(
        GQL_APPEND_TO_COMMENTS,
        {"data": {"text": "Fixed, thanks", "inReview": False}, "where": {"id": "issue_id"}},
    )
