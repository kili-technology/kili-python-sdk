"""The queue's requests are the ones the labeling interface sends."""

from kili.adapters.http_client import HttpClient
from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.adapters.kili_api_gateway.queue.operations import (
    GQL_DELETE_LOCKS,
    GQL_GET_NEXT_ASSET_FOR_REVIEW_FROM_LABEL,
    GQL_GET_NEXT_ASSET_FOR_REVIEW_FROM_PROJECT,
    GQL_GET_NEXT_ASSET_FROM_LABEL,
    GQL_GET_NEXT_ASSET_FROM_PROJECT,
    GQL_GET_PROJECT_USER,
    GQL_RENEW_LOCK,
    GQL_SEND_ASSET_BACK_TO_QUEUE,
    GQL_SKIP_ASSET,
)
from kili.core.graphql.graphql_client import GraphQLClient
from kili.domain.asset import AssetId
from kili.domain.label import LabelId
from kili.domain.project import ProjectId
from kili.domain.user import UserId


def _gateway(graphql_client: GraphQLClient, http_client: HttpClient) -> KiliAPIGateway:
    return KiliAPIGateway(graphql_client, http_client)


def test_it_asks_the_project_for_the_first_asset_to_label(graphql_client, http_client):
    # Given
    graphql_client.execute.return_value = {"data": {"id": "asset-1"}}

    # When
    asset_id = _gateway(graphql_client, http_client).get_next_asset_to_work_on(
        ProjectId("project"), review=False, viewed_asset_ids=[], given_back_asset_ids=[]
    )

    # Then
    assert asset_id == "asset-1"
    graphql_client.execute.assert_called_once_with(
        GQL_GET_NEXT_ASSET_FROM_PROJECT, {"projectID": "project"}
    )
    assert "doLock: true" in GQL_GET_NEXT_ASSET_FROM_PROJECT


def test_it_asks_from_the_assets_seen_for_the_next_ones_leaving_out_those_given_back(
    graphql_client, http_client
):
    # Given
    graphql_client.execute.return_value = {"data": None}

    # When
    asset_id = _gateway(graphql_client, http_client).get_next_asset_to_work_on(
        ProjectId("project"),
        review=False,
        viewed_asset_ids=[AssetId("a"), AssetId("b")],
        given_back_asset_ids=[AssetId("b")],
    )

    # Then
    assert asset_id is None
    graphql_client.execute.assert_called_once_with(
        GQL_GET_NEXT_ASSET_FROM_LABEL,
        {"labelAssetIDs": ["a", "b"], "nonSubmittedViewedAssetIds": ["b"], "projectId": "project"},
    )


def test_it_asks_the_review_queue_when_reviewing(graphql_client, http_client):
    # Given
    graphql_client.execute.return_value = {"data": {"id": "asset-2"}}
    gateway = _gateway(graphql_client, http_client)

    # When
    gateway.get_next_asset_to_work_on(
        ProjectId("project"), review=True, viewed_asset_ids=[], given_back_asset_ids=[]
    )
    gateway.get_next_asset_to_work_on(
        ProjectId("project"),
        review=True,
        viewed_asset_ids=[AssetId("a")],
        given_back_asset_ids=[],
    )

    # Then
    first, second = graphql_client.execute.call_args_list
    assert first.args == (GQL_GET_NEXT_ASSET_FOR_REVIEW_FROM_PROJECT, {"projectID": "project"})
    assert second.args == (
        GQL_GET_NEXT_ASSET_FOR_REVIEW_FROM_LABEL,
        {"labelAssetIDs": ["a"], "projectId": "project"},
    )


def test_it_reads_the_asset_by_its_id(graphql_client, http_client):
    # Given
    graphql_client.execute.return_value = {"data": {"id": "a", "content": "url"}}

    # When
    asset = _gateway(graphql_client, http_client).get_asset_by_id(
        AssetId("a"), fields=("id", "content")
    )

    # Then
    assert asset == {"id": "a", "content": "url"}
    query, variables = graphql_client.execute.call_args.args
    assert "asset(id: $id)" in query
    assert variables == {"id": "a"}


def test_it_reads_the_label_the_interface_opens_the_asset_with(graphql_client, http_client):
    # Given
    graphql_client.execute.side_effect = [{"data": [{"id": "l1"}]}, {"data": None}]
    gateway = _gateway(graphql_client, http_client)

    # When
    to_label = gateway.get_label_opened_with(
        AssetId("a"), UserId("me"), review=False, fields=("id",)
    )
    to_review = gateway.get_label_opened_with(
        AssetId("a"), UserId("me"), review=True, fields=("id",)
    )

    # Then
    assert to_label == {"id": "l1"}
    assert to_review is None
    (label_query, label_variables), (review_query, review_variables) = (
        call.args for call in graphql_client.execute.call_args_list
    )
    assert "getLabelsOrPredictionsForUser" in label_query
    assert label_variables == {"assetID": "a", "userID": "me"}
    assert "getLabelsToBeReviewed" in review_query
    assert review_variables == {"assetID": "a"}


def test_it_renews_and_deletes_the_lock_as_the_interface_does(graphql_client, http_client):
    # Given
    graphql_client.execute.side_effect = [
        {"data": {"lockSucceeded": True, "reasons": None}},
        {"data": "a"},
    ]
    gateway = _gateway(graphql_client, http_client)

    # When
    renewed = gateway.renew_asset_lock(ProjectId("project"), AssetId("a"))
    gateway.delete_asset_locks(ProjectId("project"), AssetId("a"))

    # Then
    assert renewed == {"lockSucceeded": True, "reasons": None}
    assert graphql_client.execute.call_args_list[0].args == (
        GQL_RENEW_LOCK,
        {"where": {"id": "a", "project": {"id": "project"}}},
    )
    assert graphql_client.execute.call_args_list[1].args == (
        GQL_DELETE_LOCKS,
        {"input": {"assetId": "a", "projectId": "project"}},
    )


def test_it_skips_with_the_reason(graphql_client, http_client):
    # Given
    graphql_client.execute.return_value = {"data": {"id": "a"}}

    # When
    _gateway(graphql_client, http_client).skip_asset_with_reason(
        ProjectId("project"), AssetId("a"), "blurry"
    )

    # Then
    graphql_client.execute.assert_called_once_with(
        GQL_SKIP_ASSET, {"where": {"id": "a", "project": {"id": "project"}}, "reason": "blurry"}
    )


def test_it_sends_back_with_the_label_under_review(graphql_client, http_client):
    # Given
    outcome = {"succeeded": [{"assetId": "a"}], "declined": [], "failed": []}
    graphql_client.execute.return_value = {"data": outcome}

    # When
    result = _gateway(graphql_client, http_client).send_asset_back_to_queue(
        ProjectId("project"), AssetId("a"), LabelId("l1")
    )

    # Then
    assert result == outcome
    graphql_client.execute.assert_called_once_with(
        GQL_SEND_ASSET_BACK_TO_QUEUE,
        {"where": {"id": "a", "project": {"id": "project"}, "label": {"id": "l1"}}},
    )


def test_it_reads_the_member_of_the_project(graphql_client, http_client):
    # Given
    graphql_client.execute.side_effect = [
        {"data": [{"role": "LABELER", "activated": True}]},
        {"data": []},
    ]
    gateway = _gateway(graphql_client, http_client)

    # When
    member = gateway.get_project_user(ProjectId("project"), UserId("me"))
    stranger = gateway.get_project_user(ProjectId("project"), UserId("other"))

    # Then
    assert member == {"role": "LABELER", "activated": True}
    assert stranger is None
    assert graphql_client.execute.call_args_list[0].args == (
        GQL_GET_PROJECT_USER,
        {"where": {"project": {"id": "project"}, "user": {"id": "me"}, "deleted": False}},
    )
