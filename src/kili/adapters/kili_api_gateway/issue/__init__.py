"""Mixin extending Kili API Gateway class with Issue related operations."""

from typing import Any, Dict, Generator, List

from kili.adapters.kili_api_gateway.base import BaseOperationMixin
from kili.adapters.kili_api_gateway.helpers.queries import (
    PaginatedGraphQLQuery,
    QueryOptions,
    fragment_builder,
)
from kili.adapters.kili_api_gateway.issue.operations import (
    GQL_COUNT_ISSUES,
    GQL_CREATE_ISSUES,
)
from kili.adapters.kili_api_gateway.issue.types import IssueToCreateKiliAPIGatewayInput
from kili.core.constants import MUTATION_BATCH_SIZE
from kili.core.utils.pagination import batcher
from kili.domain.issue import IssueFilters, IssueId, IssueStatus, IssueType
from kili.domain.types import ListOrTuple
from kili.utils import tqdm

from .mappers import issue_where_mapper
from .operations import GQL_UPDATE_ISSUE, get_issues_query


class IssueOperationMixin(BaseOperationMixin):
    """GraphQL Mixin extending GraphQL Gateway class with Issue related operations."""

    def create_issues(
        self, type_: IssueType, issues: List[IssueToCreateKiliAPIGatewayInput], description: str
    ) -> List[IssueId]:
        """Send a GraphQL request calling createIssues resolver."""
        created_issue_entities: List[IssueId] = []
        with tqdm.tqdm(total=len(issues), desc=description) as pbar:
            for issues_batch in batcher(issues, batch_size=MUTATION_BATCH_SIZE):
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

    def list_issues(
        self, filters: IssueFilters, fields: ListOrTuple[str], options: QueryOptions
    ) -> Generator[Dict, None, None]:
        """Send a GraphQL request calling issues resolver."""
        fragment = fragment_builder(fields)
        query = get_issues_query(fragment)
        where = issue_where_mapper(filters=filters)
        return PaginatedGraphQLQuery(self.graphql_client).execute_query_from_paginated_call(
            query, where, options, "Retrieving issues", GQL_COUNT_ISSUES
        )

    def update_issue_status(self, issue_id: IssueId, status: IssueStatus) -> Dict[str, Any]:
        """Update the status of an issue."""
        data = {"status": status}
        where = {"id": issue_id}
        payload = {"data": data, "where": where}
        return self.graphql_client.execute(GQL_UPDATE_ISSUE, payload)
