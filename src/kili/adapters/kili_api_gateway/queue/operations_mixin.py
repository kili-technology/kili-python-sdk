"""Mixin extending Kili API Gateway class with the requests serving a member their queue."""

import json
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
    GQL_SUBMIT_LABEL,
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
        so far, the ones left without a submit passed over. The interface sends every asset of its
        session; a script's session can be the whole queue, so only what the backend reads is sent.
        """
        if not viewed_asset_ids:
            query = (
                GQL_GET_NEXT_ASSET_FOR_REVIEW_FROM_PROJECT
                if review
                else GQL_GET_NEXT_ASSET_FROM_PROJECT
            )
            variables: dict = {"projectID": project_id}
        elif review:
            # every id sent is passed over: the last one seen — the first, which locates the
            # project — and those given back
            query = GQL_GET_NEXT_ASSET_FOR_REVIEW_FROM_LABEL
            ignored = [viewed_asset_ids[-1], *given_back_asset_ids]
            variables = {"labelAssetIDs": list(dict.fromkeys(ignored)), "projectId": project_id}
        else:
            # the seen assets only locate the project, the last one is enough; those given back
            # are passed over
            query = GQL_GET_NEXT_ASSET_FROM_LABEL
            variables = {
                "labelAssetIDs": [viewed_asset_ids[-1]],
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

    # pylint: disable=too-many-arguments
    def submit_label(
        self,
        asset_id: AssetId,
        author_id: UserId,
        json_response: dict,
        label_type: str,
        seconds_to_label: int,
        referenced_label_id: Optional[LabelId],
    ) -> dict:
        """Submit a label as the labeling and review interfaces submit it.

        `frontendAppendToLabels` addressed by the asset's id, with the label the asset was opened
        with as its reference: the mutations addressing assets by a list of ids only reach those a
        labeler already labeled, and `appendToLabels` drops the reference that limits a step
        group's allowed-jobs check to what the label changes.
        """
        data: dict = {
            "authorID": author_id,
            "jsonResponse": json.dumps(json_response),
            "labelType": label_type,
            "secondsToLabel": seconds_to_label,
        }
        if referenced_label_id is not None:
            data["referencedLabelId"] = referenced_label_id
        result = self.graphql_client.execute(
            GQL_SUBMIT_LABEL, {"data": data, "where": {"id": asset_id}}
        )
        return result["data"]

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
