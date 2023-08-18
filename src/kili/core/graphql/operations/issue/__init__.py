"""GraphQL Mixin extending GraphQL Gateway class with Issue related operations."""

from dataclasses import dataclass
from typing import List, Optional

from kili.core.enums import IssueStatus
from kili.core.graphql.graphql_client import GraphQLClient
from kili.core.graphql.operations.issue.operations import (
    GQL_COUNT_ISSUES,
    GQL_CREATE_ISSUES,
)
from kili.core.graphql.operations.issue.types import IssueToCreateGQLGatewayInput
from kili.core.utils.pagination import BatchIteratorBuilder
from kili.domain.issues import Issue, IssueType


@dataclass
class IssueWhere:
    """Tuple to be passed to the IssueQuery to restrict query."""

    project_id: str
    asset_id: Optional[str] = None
    asset_id_in: Optional[List[str]] = None
    issue_type: Optional[IssueType] = None
    status: Optional[IssueStatus] = None

    def get_graphql_input(self):
        """Build the GraphQL Where payload sent in the resolver from the SDK IssueWhere."""
        return {
            "project": {"id": self.project_id},
            "asset": {"id": self.asset_id},
            "assetIn": self.asset_id_in,
            "status": self.status,
            "type": self.issue_type,
        }


class IssueOperationMixin:
    """GraphQL Mixin extending GraphQL Gateway class with Issue related operations."""

    graphql_client: GraphQLClient

    def create_issues(
        self, type_: IssueType, issues: List[IssueToCreateGQLGatewayInput]
    ) -> List[Issue]:
        created_issues_ids: List[str] = []
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
        return [Issue(id=id) for id in created_issues_ids]

    def count_issues(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_id_in: Optional[List[str]] = None,
        issue_type: Optional[IssueType] = None,
        status: Optional[IssueStatus] = None,
    ):
        where = IssueWhere(project_id, asset_id, asset_id_in, issue_type, status)
        payload = {
            "where": where.get_graphql_input(),
        }
        count_result = self.graphql_client.execute(GQL_COUNT_ISSUES, payload)
        return count_result["data"]
