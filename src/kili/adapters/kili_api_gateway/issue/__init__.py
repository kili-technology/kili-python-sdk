"""Mixin extending Kili API Gateway class with Issue related operations."""

from typing import List

from kili.adapters.kili_api_gateway.base import BaseOperationMixin
from kili.adapters.kili_api_gateway.issue.mappers import issue_where_mapper
from kili.adapters.kili_api_gateway.issue.operations import (
    GQL_COUNT_ISSUES,
    GQL_CREATE_ISSUES,
)
from kili.adapters.kili_api_gateway.issue.types import IssueToCreateKiliAPIGatewayInput
from kili.core.utils.pagination import BatchIteratorBuilder
from kili.domain.issue import IssueFilters, IssueId, IssueType
from kili.utils import tqdm


class IssueOperationMixin(BaseOperationMixin):
    """GraphQL Mixin extending GraphQL Gateway class with Issue related operations."""

    def create_issues(
        self, type_: IssueType, issues: List[IssueToCreateKiliAPIGatewayInput]
    ) -> List[IssueId]:
        """Send a GraphQL request calling createIssues resolver."""
        created_issue_entities: List[IssueId] = []
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
                    [IssueId(issue["id"]) for issue in batch_created_issues]
                )
                pbar.update(len(issues_batch))
        return created_issue_entities

    def count_issues(self, filters: IssueFilters) -> int:
        """Send a GraphQL request calling countIssues resolver."""
        where = issue_where_mapper(filters)
        payload = {"where": where}
        count_result = self.graphql_client.execute(GQL_COUNT_ISSUES, payload)
        return count_result["data"]
