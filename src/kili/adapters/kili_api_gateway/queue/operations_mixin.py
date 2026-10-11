"""Mixin extending Kili API Gateway class with the requests serving a member their queue."""

from typing import Optional

from kili.adapters.kili_api_gateway.base import BaseOperationMixin
from kili.adapters.kili_api_gateway.helpers.queries import fragment_builder
from kili.domain.asset import AssetId
from kili.domain.label import LabelId
from kili.domain.project import ProjectId
from kili.domain.types import ListOrTuple
from kili.domain.user import UserId

from .operations import (
    GQL_DELETE_LOCKS,
    GQL_GET_NEXT_ASSET_FOR_REVIEW_FROM_LABEL,
    GQL_GET_NEXT_ASSET_FOR_REVIEW_FROM_PROJECT,
    GQL_GET_NEXT_ASSET_FROM_LABEL,
    GQL_GET_NEXT_ASSET_FROM_PROJECT,
    GQL_GET_PROJECT_USER,
    GQL_RENEW_LOCK,
    GQL_SEND_ASSET_BACK_TO_QUEUE,
    GQL_SKIP_ASSET,
    get_asset_query,
    get_label_for_user_query,
    get_label_to_review_query,
)


class QueueOperationMixin(BaseOperationMixin):
    """GraphQL Mixin extending GraphQL Gateway class with the queue's requests."""

    def get_next_asset_to_work_on(
        self,
        project_id: ProjectId,
        review: bool,
        viewed_asset_ids: ListOrTuple[AssetId],
        given_back_asset_ids: ListOrTuple[AssetId],
    ) -> Optional[AssetId]:
        """Ask for the member's next asset, locked to them, as the labeling interface asks for it.

        The interface's first asset comes from the project; every later one from the assets seen
        so far, the ones left without a submit excluded (labeling) or every one seen (review).
        """
        if not viewed_asset_ids:
            query = (
                GQL_GET_NEXT_ASSET_FOR_REVIEW_FROM_PROJECT
                if review
                else GQL_GET_NEXT_ASSET_FROM_PROJECT
            )
            variables: dict = {"projectID": project_id}
        elif review:
            query = GQL_GET_NEXT_ASSET_FOR_REVIEW_FROM_LABEL
            variables = {"labelAssetIDs": list(viewed_asset_ids), "projectId": project_id}
        else:
            query = GQL_GET_NEXT_ASSET_FROM_LABEL
            variables = {
                "labelAssetIDs": list(viewed_asset_ids),
                "nonSubmittedViewedAssetIds": list(given_back_asset_ids),
                "projectId": project_id,
            }
        result = self.graphql_client.execute(query, variables)
        asset = result["data"]
        return AssetId(asset["id"]) if asset else None

    def get_asset_by_id(self, asset_id: AssetId, fields: ListOrTuple[str]) -> dict:
        """Read one asset by its id, as the interface reads the asset it serves."""
        query = get_asset_query(fragment_builder(fields))
        result = self.graphql_client.execute(query, {"id": asset_id})
        return result["data"]

    def get_label_opened_with(
        self,
        asset_id: AssetId,
        user_id: UserId,
        review: bool,
        fields: ListOrTuple[str],
    ) -> Optional[dict]:
        """Read the label the labeling (or review) interface opens the asset with, if any."""
        fragment = fragment_builder(fields)
        if review:
            query = get_label_to_review_query(fragment)
            variables: dict = {"assetID": asset_id}
        else:
            query = get_label_for_user_query(fragment)
            variables = {"assetID": asset_id, "userID": user_id}
        result = self.graphql_client.execute(query, variables)
        labels = result["data"] or []
        return labels[0] if labels else None

    def renew_asset_lock(self, project_id: ProjectId, asset_id: AssetId) -> dict:
        """Take, or renew, the member's lock on the asset; says whether it holds and why not."""
        variables = {"where": {"id": asset_id, "project": {"id": project_id}}}
        result = self.graphql_client.execute(GQL_RENEW_LOCK, variables)
        return result["data"]

    def delete_asset_locks(self, project_id: ProjectId, asset_id: AssetId) -> None:
        """Release the member's lock on the asset."""
        variables = {"input": {"assetId": asset_id, "projectId": project_id}}
        self.graphql_client.execute(GQL_DELETE_LOCKS, variables)

    def skip_asset_with_reason(self, project_id: ProjectId, asset_id: AssetId, reason: str) -> None:
        """Skip the asset, with the reason the labeling interface's skip asks for."""
        variables = {"where": {"id": asset_id, "project": {"id": project_id}}, "reason": reason}
        self.graphql_client.execute(GQL_SKIP_ASSET, variables)

    def send_asset_back_to_queue(
        self, project_id: ProjectId, asset_id: AssetId, label_id: Optional[LabelId]
    ) -> dict:
        """Send the asset back with the label under review, as the review dialog's Send back does."""
        where: dict = {"id": asset_id, "project": {"id": project_id}}
        if label_id is not None:
            where["label"] = {"id": label_id}
        result = self.graphql_client.execute(GQL_SEND_ASSET_BACK_TO_QUEUE, {"where": where})
        return result["data"]

    def get_project_user(self, project_id: ProjectId, user_id: UserId) -> Optional[dict]:
        """Return the member's role in the project, or None when they are not one."""
        where = {"project": {"id": project_id}, "user": {"id": user_id}, "deleted": False}
        result = self.graphql_client.execute(GQL_GET_PROJECT_USER, {"where": where})
        project_users = result["data"] or []
        return project_users[0] if project_users else None
