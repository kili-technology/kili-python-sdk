from kili.adapters.http_client import HttpClient
from kili.adapters.kili_api_gateway.issue import IssueOperationMixin
from kili.adapters.kili_api_gateway.issue.operations import GQL_CREATE_ISSUES
from kili.adapters.kili_api_gateway.issue.types import IssueToCreateKiliAPIGatewayInput
from kili.core.graphql.graphql_client import GraphQLClient
from kili.core.graphql.operations.label.queries import LabelQuery
from kili.domain.asset import AssetId
from kili.domain.label import LabelId
from kili.domain.project import ProjectId


def test_create_issue(mocker, mocked_graphql_client: GraphQLClient, mocked_http_client: HttpClient):
    # Given
    issue = IssueToCreateKiliAPIGatewayInput(
        label_id="label_id",
        text="text",
        object_mid="object_mid",
    )

    issue_operations = IssueOperationMixin()
    issue_operations.graphql_client = mocked_graphql_client
    issue_operations.http_client = mocked_http_client
    mocker.patch.object(
        issue_operations,
        "_get_labels_asset_ids_map",
        return_value={LabelId("label_id"): AssetId("asset_id")},
    )

    # When
    issue_operations.create_issues(project_id=ProjectId("project_id"), issues=[issue])

    # Then
    payload = {
        "issues": [
            {
                "issueNumber": 0,
                "labelID": issue.label_id,
                "objectMid": issue.object_mid,
                "type": "ISSUE",
                "assetId": "asset_id",
                "text": issue.text,
            }
        ],
        "where": {"idIn": ["asset_id"]},
    }
    issue_operations.graphql_client.execute.assert_called_with(GQL_CREATE_ISSUES, payload)


def test_get_labels_asset_ids_map(
    mocker, mocked_graphql_client: GraphQLClient, mocked_http_client: HttpClient
):
    # Given
    issue_operations = IssueOperationMixin()
    issue_operations.graphql_client = mocked_graphql_client
    issue_operations.http_client = mocked_http_client

    with mocker.patch.object(
        LabelQuery,
        "__call__",
        return_value=iter(
            [
                {"id": "label_id_1", "labelOf": {"id": "asset_id_1"}},
                {"id": "label_id_2", "labelOf": {"id": "asset_id_1"}},
            ]
        ),
    ):
        # When
        labels_id_map = issue_operations._get_labels_asset_ids_map(
            ProjectId("project_id"),
            [LabelId("label_id_1"), LabelId("label_id_2")],
        )

        # Then
        assert labels_id_map == {
            "label_id_1": "asset_id_1",
            "label_id_2": "asset_id_1",
        }
