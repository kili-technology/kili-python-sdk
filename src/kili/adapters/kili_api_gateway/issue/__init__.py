"""Mixin extending Kili API Gateway class with Issue related operations."""

from typing import Dict, List

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.adapters.kili_api_gateway.issue.mappers import issue_where_mapper
from kili.adapters.kili_api_gateway.issue.operations import (
    GQL_COUNT_ISSUES,
    GQL_CREATE_ISSUES,
)
from kili.adapters.kili_api_gateway.issue.types import IssueToCreateKiliAPIGatewayInput
from kili.core.graphql.operations.label.queries import LabelQuery, LabelWhere
from kili.core.utils.pagination import BatchIteratorBuilder
from kili.domain.asset import AssetId
from kili.domain.issue import IssueFilters, IssueId
from kili.domain.label import LabelId
from kili.domain.project import ProjectId
from kili.exceptions import NotFound
from kili.utils import tqdm

from ..base import BaseOperationMixin


class IssueOperationMixin(BaseOperationMixin):
    """GraphQL Mixin extending GraphQL Gateway class with Issue related operations."""

    def create_issues(
        self,
        project_id: ProjectId,
        issues: List[IssueToCreateKiliAPIGatewayInput],
    ) -> List[IssueId]:
        """Send a GraphQL request calling createIssues resolver."""
        created_issue_entities: List[IssueId] = []
        label_asset_ids_map = self._get_labels_asset_ids_map(
            project_id, [LabelId(issue.label_id) for issue in issues]
        )  # TODO: should be done in the backend
        with tqdm.tqdm(total=len(issues), desc="Creating issues") as pbar:
            for issues_batch in BatchIteratorBuilder(issues):
                batch_targeted_asset_ids = [
                    label_asset_ids_map[LabelId(issue.label_id)] for issue in issues_batch
                ]
                payload = {
                    "issues": [
                        {
                            "issueNumber": 0,
                            "labelID": issue.label_id,
                            "objectMid": issue.object_mid,
                            "type": "ISSUE",
                            "assetId": str(label_asset_ids_map[LabelId(issue.label_id)]),
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

    def _get_labels_asset_ids_map(
        self,
        project_id: ProjectId,
        label_id_array: List[LabelId],
    ) -> Dict[LabelId, AssetId]:
        """Return a dictionary that gives for every label id, its associated asset id.

        Args:
            kili_api_gateway: instance of KiliAPIGateway
            project_id: id of the project
            label_id_array: list of label ids

        Returns:
            a dict of key->value a label id->its associated asset id for the given label ids

        Raises:
            NotFound error if at least one label was not found with its given id
        """
        options = QueryOptions(disable_tqdm=True)
        where = LabelWhere(
            project_id=project_id,
            id_contains=[str(lab) for lab in label_id_array],
        )
        labels = list(
            LabelQuery(self.graphql_client, self.http_client)(
                where=where, fields=["labelOf.id", "id"], options=options
            )
        )
        labels_not_found = [
            label_id
            for label_id in label_id_array
            if label_id not in [label["id"] for label in labels]
        ]
        if len(labels_not_found) > 0:
            raise NotFound(str(labels_not_found))
        return {LabelId(label["id"]): AssetId(label["labelOf"]["id"]) for label in labels}
