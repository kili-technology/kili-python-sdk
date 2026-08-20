"""Tests for the asset mutations."""

import pytest
import pytest_mock

from kili.entrypoints.mutations.asset import MutationsAsset, PageResolution
from kili.exceptions import DeprecatedArgumentError, GraphQLError


@pytest.mark.parametrize(
    "page_resolutions_array",
    [
        [
            [
                {"width": 100, "height": 200, "pageNumber": 1},
                {"width": 200, "height": 300, "pageNumber": 0},
            ]
        ],
        [
            [
                PageResolution(width=100, height=200, page_number=1),
                PageResolution(width=200, height=300, page_number=0),
            ]
        ],
    ],
)
def test_given_page_resolutions_when_i_call_update_properties_in_assets_it_calls_the_resolvers_correctly(
    page_resolutions_array,
    mocker: pytest_mock.MockerFixture,
):
    """Test update_properties_in_assets for resolution update."""
    # Given
    kili = MutationsAsset()
    kili.graphql_client = mocker.MagicMock()
    kili.http_client = mocker.MagicMock()
    kili.kili_api_gateway = mocker.MagicMock()

    asset_ids = ["asset_id"]

    # When
    kili.update_properties_in_assets(
        asset_ids=asset_ids, page_resolutions_array=page_resolutions_array
    )

    # Then
    kili.graphql_client.execute.assert_called_once_with(
        "\nmutation(\n    $whereArray: [AssetWhere!]!\n    $dataArray: [AssetData!]!\n) {\n"
        "  data: updatePropertiesInAssets(\n    where: $whereArray,\n    data: $dataArray\n"
        "  ) {\n    id\n  }\n}\n",
        {
            "whereArray": [{"id": "asset_id"}],
            "dataArray": [
                {
                    "pageResolutions": [
                        {"width": 100, "height": 200, "pageNumber": 1},
                        {"width": 200, "height": 300, "pageNumber": 0},
                    ],
                }
            ],
        },
    )


def test_given_asset_resolution_when_updating_resolution_then_it_works(
    mocker: pytest_mock.MockerFixture,
):
    # Given
    kili = MutationsAsset()
    kili.graphql_client = mocker.MagicMock()
    kili.http_client = mocker.MagicMock()
    kili.kili_api_gateway = mocker.MagicMock()

    # When
    kili.update_properties_in_assets(
        asset_ids=["asset_id_1"], resolution_array=[{"width": 100, "height": 200}]
    )

    # Then
    assert kili.graphql_client.execute.call_args[0][1] == {
        "whereArray": [{"id": "asset_id_1"}],
        "dataArray": [{"resolution": {"width": 100, "height": 200}}],
    }


def _backend_error(message: str) -> GraphQLError:
    """Build the error the graphql client raises when the backend refuses the mutation."""
    return GraphQLError(
        error=[
            {
                "message": message,
                "extensions": {
                    "code": "OPERATION_RESOLUTION_FAILURE",
                    "context": {"projectID": "project_id"},
                },
            }
        ]
    )


def test_given_multi_review_project_when_i_use_is_used_for_consensus_then_i_get_a_clear_error(
    mocker: pytest_mock.MockerFixture,
):
    # Given
    kili = MutationsAsset()
    kili.graphql_client = mocker.MagicMock()
    kili.http_client = mocker.MagicMock()
    kili.kili_api_gateway = mocker.MagicMock()
    kili.graphql_client.execute.side_effect = _backend_error(
        "[isUsedForConsensusDeprecated] `isUsedForConsensus` is deprecated in"
        " `update_properties_in_assets`. Use `update_asset_consensus` instead to manage consensus"
        " for this asset."
    )

    # When
    with pytest.raises(DeprecatedArgumentError) as exc_info:
        kili.update_properties_in_assets(
            asset_ids=["asset_id_1"], is_used_for_consensus_array=[True]
        )

    # Then
    assert str(exc_info.value) == (
        "`isUsedForConsensus` is deprecated in `update_properties_in_assets`."
        " Use `update_asset_consensus` instead to manage consensus for this asset."
    )
    assert isinstance(exc_info.value.__cause__, GraphQLError)
    assert "[isUsedForConsensusDeprecated]" in str(exc_info.value.__cause__)


def test_given_workflow_v1_project_when_i_use_is_used_for_consensus_then_the_field_is_sent(
    mocker: pytest_mock.MockerFixture,
):
    # Given
    kili = MutationsAsset()
    kili.graphql_client = mocker.MagicMock()
    kili.http_client = mocker.MagicMock()
    kili.kili_api_gateway = mocker.MagicMock()

    # When
    kili.update_properties_in_assets(
        asset_ids=["asset_id_1", "asset_id_2"], is_used_for_consensus_array=[True, False]
    )

    # Then
    assert kili.graphql_client.execute.call_args[0][1] == {
        "whereArray": [{"id": "asset_id_1"}, {"id": "asset_id_2"}],
        "dataArray": [{"isUsedForConsensus": True}, {"isUsedForConsensus": False}],
    }


def test_given_an_unrelated_backend_error_when_i_update_properties_then_it_is_not_converted(
    mocker: pytest_mock.MockerFixture,
):
    # Given
    kili = MutationsAsset()
    kili.graphql_client = mocker.MagicMock()
    kili.http_client = mocker.MagicMock()
    kili.kili_api_gateway = mocker.MagicMock()
    kili.graphql_client.execute.side_effect = _backend_error("[somethingElse] Another failure")

    # When / Then
    with pytest.raises(GraphQLError):
        kili.update_properties_in_assets(asset_ids=["asset_id_1"], priorities=[1])
