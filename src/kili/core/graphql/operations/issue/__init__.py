"""GraphQL Mixin extending GraphQL Gateway class with Issue related operations."""

from typing import List

from kili.core.graphql.graphql_client import GraphQLClient
from kili.core.graphql.operations.issue.operations import GQL_CREATE_ISSUES
from kili.core.graphql.operations.issue.types import IssueToCreateGraphQLGatewayInput
from kili.core.utils.pagination import BatchIteratorBuilder
from kili.domain.issues import IssueType


class IssueOperationMixin:
    """GraphQL Mixin extending GraphQL Gateway class with Issue related operations."""

    graphql_client: GraphQLClient

    def create_issues(self, type_: IssueType, issues: List[IssueToCreateGraphQLGatewayInput]):
        created_issues_ids = []
        for issues_batch in BatchIteratorBuilder(issues):
            batch_targeted_asset_ids = [issue.asset_id for issue in issues_batch]
            payload = {
                "issues": [
                    {
                        "issueNumber": issue.issue_number,
                        "labelID": issue.label_id,
                        "objectMid": issue.object_mid,
                        "type": type_,
                        "assetId": issue.asset_id,
                        "text": issue.text,
                    }
                    for issue in issues_batch
                ],
                "where": {"idIn": batch_targeted_asset_ids},
            }
            result = self.graphql_client.execute(GQL_CREATE_ISSUES, payload)
            batch_created_issues_ids = result["data"]
            created_issues_ids.extend(batch_created_issues_ids)
        return created_issues_ids
