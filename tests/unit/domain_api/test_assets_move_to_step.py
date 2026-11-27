"""Tests for kili.assets.move_to_next_step and its to_step_id."""

from unittest.mock import MagicMock

import pytest

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.domain_api.assets import AssetsNamespace
from kili.exceptions import GraphQLError

OUTCOME = {
    "succeeded": [{"assetId": "asset-1", "externalId": "image-1"}],
    "declined": [],
    "failed": [],
}


@pytest.fixture()
def legacy_client():
    return MagicMock()


@pytest.fixture()
def gateway():
    gateway = MagicMock(spec=KiliAPIGateway)
    gateway.graphql_client = MagicMock()
    gateway.graphql_client.execute.return_value = {"data": OUTCOME}
    return gateway


@pytest.fixture()
def assets(legacy_client, gateway):
    return AssetsNamespace(legacy_client, gateway)


def test_move_to_a_chosen_step_sends_it_as_the_step_id(assets, legacy_client, gateway):
    outcome = assets.move_to_next_step(asset_ids=["asset-1"], to_step_id="review-2")

    assert outcome == OUTCOME
    document, variables = gateway.graphql_client.execute.call_args.args
    assert "addAssetsToReview(where: $where, stepId: $stepId)" in document
    assert variables == {"stepId": "review-2", "where": {"idIn": ["asset-1"]}}
    legacy_client.add_to_review.assert_not_called()


def test_move_without_a_step_is_unchanged(assets, legacy_client, gateway):
    legacy_client.add_to_review.return_value = OUTCOME

    outcome = assets.move_to_next_step(asset_id="asset-1")

    assert outcome == OUTCOME
    legacy_client.add_to_review.assert_called_once_with(
        asset_ids=["asset-1"], external_ids=None, project_id=""
    )
    gateway.graphql_client.execute.assert_not_called()


def test_move_to_a_chosen_step_explains_a_server_that_predates_it(assets, gateway):
    gateway.graphql_client.execute.side_effect = GraphQLError(
        'Unknown argument "stepId" on field "Mutation.addAssetsToReview".'
    )

    with pytest.raises(GraphQLError, match=r"move_to_next_step\(to_step_id=...\) needs a version"):
        assets.move_to_next_step(asset_ids=["asset-1"], to_step_id="review-2")


def test_move_to_a_chosen_step_with_no_asset_does_nothing(assets, gateway):
    with pytest.warns(UserWarning):
        outcome = assets.move_to_next_step(asset_ids=[], to_step_id="review-2")

    assert outcome == {"succeeded": [], "declined": [], "failed": []}
    gateway.graphql_client.execute.assert_not_called()
