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

    asset_ids = ["asset_id"]

    # When
    kili.update_properties_in_assets(
        asset_ids=asset_ids, page_resolutions_array=page_resolutions_array
    )

    # Then
    kili.graphql_client.execute.assert_called_once_with(
        (
            "\nmutation(\n    $whereArray: [AssetWhere!]!\n    $dataArray: [AssetData!]!\n) {\n"
            "  data: updatePropertiesInAssets(\n    where: $whereArray,\n    data: $dataArray\n"
            "  ) {\n    id\n  }\n}\n"
        ),
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
