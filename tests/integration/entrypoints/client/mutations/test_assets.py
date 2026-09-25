"""Tests for the asset mutations."""

import pytest
import pytest_mock

from kili.entrypoints.mutations.asset import MutationsAsset, PageResolution


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


def test_given_assets_in_several_batches_when_i_assign_them_it_merges_what_each_call_reported(
    mocker: pytest_mock.MockerFixture,
):
    """The caller is told what happened to its assets, not how they were batched."""
    # Given two assignee combinations, so the mutation is called twice
    kili = MutationsAsset()
    kili.graphql_client = mocker.MagicMock()
    kili.http_client = mocker.MagicMock()
    kili.kili_api_gateway = mocker.MagicMock()

    kili.graphql_client.execute.side_effect = [
        {
            "data": {
                "declined": [],
                "failed": [],
                "succeeded": [{"assetId": "asset_1", "externalId": "img_0001"}],
            }
        },
        {
            "data": {
                "declined": [{"assetId": "asset_2", "externalId": "img_0042"}],
                "failed": [],
                "succeeded": [],
            }
        },
    ]

    # When
    outcome = kili.assign_assets_to_labelers(
        asset_ids=["asset_1", "asset_2"],
        to_be_labeled_by_array=[["user_1"], ["user_2"]],
    )

    # Then the two calls come back as one outcome, the labeler kept at work among it
    assert kili.graphql_client.execute.call_count == 2
    assert outcome == {
        "declined": [{"assetId": "asset_2", "externalId": "img_0042"}],
        "failed": [],
        "succeeded": [{"assetId": "asset_1", "externalId": "img_0001"}],
    }


def test_given_no_asset_when_i_assign_it_reports_an_empty_outcome(
    mocker: pytest_mock.MockerFixture,
):
    """The empty shortcut has to return what the caller will index into anyway."""
    # Given
    kili = MutationsAsset()
    kili.graphql_client = mocker.MagicMock()
    kili.http_client = mocker.MagicMock()
    kili.kili_api_gateway = mocker.MagicMock()

    # When
    outcome = kili.assign_assets_to_labelers(asset_ids=[], to_be_labeled_by_array=[])

    # Then
    assert outcome == {"declined": [], "failed": [], "succeeded": []}
    kili.graphql_client.execute.assert_not_called()


@pytest.mark.parametrize(
    ("method", "mutation"),
    [
        ("delete_many_from_dataset", "deleteAssets"),
    ],
)
def test_given_more_assets_than_a_batch_when_i_run_a_queue_action_it_merges_what_each_call_reported(
    mocker: pytest_mock.MockerFixture, method: str, mutation: str
):
    """The caller is told what happened to its assets, not how they were batched."""
    # Given 101 assets, so the mutation is called twice
    kili = MutationsAsset()
    kili.graphql_client = mocker.MagicMock()
    kili.http_client = mocker.MagicMock()
    kili.kili_api_gateway = mocker.MagicMock()
    asset_ids = [f"asset_{index}" for index in range(101)]

    kili.graphql_client.execute.side_effect = [
        {
            "data": {
                "declined": [],
                "failed": [{"assetId": "asset_0", "externalId": "img_0", "details": "Retry."}],
                "succeeded": [{"assetId": "asset_1", "externalId": "img_1"}],
            }
        },
        {
            "data": {
                "declined": [{"assetId": "asset_100", "externalId": "img_100"}],
                "failed": [],
                "succeeded": [],
            }
        },
    ]

    # When
    outcome = getattr(kili, method)(asset_ids=asset_ids)

    # Then each batch named its own assets, through the mutation that reports them
    assert kili.graphql_client.execute.call_count == 2
    (first_query, first_variables), _ = kili.graphql_client.execute.call_args_list[0]
    (_, second_variables), _ = kili.graphql_client.execute.call_args_list[1]
    assert f"{mutation}(where: $where)" in first_query
    assert first_variables == {"where": {"idIn": asset_ids[:100]}}
    assert second_variables == {"where": {"idIn": asset_ids[100:]}}
    assert outcome == {
        "declined": [{"assetId": "asset_100", "externalId": "img_100"}],
        "failed": [{"assetId": "asset_0", "externalId": "img_0", "details": "Retry."}],
        "succeeded": [{"assetId": "asset_1", "externalId": "img_1"}],
    }
