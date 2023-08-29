"""Mixin extending Kili API Gateway class with Issue related operations."""

from typing import List, Optional

from kili.core.graphql.graphql_client import GraphQLClient
from kili.core.utils.pagination import BatchIteratorBuilder
from kili.domain.issue import Issue, IssueStatus, IssueType
from kili.gateways.kili_api_gateway.issue.operations import (
    GQL_COUNT_ISSUES,
    GQL_CREATE_ISSUES,
)
from kili.gateways.kili_api_gateway.issue.types import (
    IssueToCreateKiliAPIGatewayInput,
    IssueWhere,
)
from kili.utils import tqdm


class IssueOperationMixin:
    """GraphQL Mixin extending GraphQL Gateway class with Issue related operations."""

    graphql_client: GraphQLClient

    def create_issues(
        self, type_: IssueType, issues: List[IssueToCreateKiliAPIGatewayInput]
    ) -> List[Issue]:
        """Send a GraphQL request calling createIssues resolver."""
        created_issue_entities: List[Issue] = []
        with tqdm.tqdm(total=len(issues), desc="Creating issues") as pbar:
            for issues_batch in BatchIteratorBuilder(issues):
                batch_targeted_asset_ids = [issue.asset_id for issue in issues_batch]
                payload = {
                    "issues": [
                        {
                            "issueNumber": 0,
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
                batch_created_issues = result["data"]
                created_issue_entities.extend(
                    [Issue(id_=issue["id"]) for issue in batch_created_issues]
                )
                pbar.update(len(issues_batch))
        return created_issue_entities

    def count_issues(  # pylint: disable=too-many-arguments,
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_id_in: Optional[List[str]] = None,
        issue_type: Optional[IssueType] = None,
        status: Optional[IssueStatus] = None,
    ) -> int:
        """Send a GraphQL request calling countIssues resolver."""
        where = IssueWhere(project_id, asset_id, asset_id_in, issue_type, status)
        payload = {
            "where": where.get_graphql_where_value(),
        }
        count_result = self.graphql_client.execute(GQL_COUNT_ISSUES, payload)
        return count_result["data"]
