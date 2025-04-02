"""Tests for asset metadata functions."""

import pytest_mock

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.domain.asset import AssetFilters
from kili.domain.project import ProjectId
from kili.entrypoints.mutations.asset import MutationsAsset


def test_add_metadata_adds_to_existing_metadata(mocker: pytest_mock.MockerFixture):
    """Test that add_metadata adds new metadata without removing existing metadata."""
    kili_api_gateway = mocker.Mock(spec=KiliAPIGateway)

    existing_assets = [
        {
            "id": "asset1",
            "jsonMetadata": {"text": "Some text", "assetLabelingMetadata": {"existing1": "value1"}},
        },
        {
            "id": "asset2",
            "jsonMetadata": {
                "imageUrl": "http://example.com/image.jpg",
                "assetLabelingMetadata": {"existing2": "value2"},
            },
        },
    ]

    kili_api_gateway.list_assets.return_value = existing_assets

    update_mock = mocker.patch.object(MutationsAsset, "update_properties_in_assets")
    update_mock.return_value = [{"id": "asset1"}, {"id": "asset2"}]

    mutations_asset = MutationsAsset()
    mutations_asset.kili_api_gateway = kili_api_gateway
    mutations_asset.graphql_client = mocker.Mock()

    project_id = "project1"
    asset_ids = ["asset1", "asset2"]
    new_metadata = [{"new_key1": "new_value1"}, {"new_key2": "new_value2"}]

    result = mutations_asset.add_metadata(
        asset_labeling_metadata=new_metadata, asset_ids=asset_ids, project_id=project_id
    )

    kili_api_gateway.list_assets.assert_called_once_with(
        AssetFilters(project_id=ProjectId(project_id), asset_id_in=asset_ids),
        ["id", "jsonMetadata"],
        QueryOptions(disable_tqdm=True),
    )

    update_mock.assert_called_once()
    call_args = update_mock.call_args[1]

    assert call_args["asset_ids"] == asset_ids

    expected_metadata = [
        {
            "text": "Some text",
            "assetLabelingMetadata": {"existing1": "value1", "new_key1": "new_value1"},
        },
        {
            "imageUrl": "http://example.com/image.jpg",
            "assetLabelingMetadata": {"existing2": "value2", "new_key2": "new_value2"},
        },
    ]

    assert call_args["json_metadatas"] == expected_metadata
    assert result == [{"id": "asset1"}, {"id": "asset2"}]


def test_set_metadata_replaces_existing_metadata(mocker: pytest_mock.MockerFixture):
    """Test that set_metadata replaces existing metadata."""
    kili_api_gateway = mocker.Mock(spec=KiliAPIGateway)

    existing_assets = [
        {
            "id": "asset1",
            "jsonMetadata": {
                "text": "Some text",
                "assetLabelingMetadata": {"existing1": "value1", "should_be_removed": True},
            },
        },
        {
            "id": "asset2",
            "jsonMetadata": {
                "imageUrl": "http://example.com/image.jpg",
                "assetLabelingMetadata": {"existing2": "value2", "also_remove": "yes"},
            },
        },
    ]

    kili_api_gateway.list_assets.return_value = existing_assets

    update_mock = mocker.patch.object(MutationsAsset, "update_properties_in_assets")
    update_mock.return_value = [{"id": "asset1"}, {"id": "asset2"}]

    mutations_asset = MutationsAsset()
    mutations_asset.kili_api_gateway = kili_api_gateway
    mutations_asset.graphql_client = mocker.Mock()

    project_id = "project1"
    asset_ids = ["asset1", "asset2"]
    new_metadata = [{"new_key1": "new_value1"}, {"new_key2": "new_value2"}]

    result = mutations_asset.set_metadata(
        asset_labeling_metadata=new_metadata, asset_ids=asset_ids, project_id=project_id
    )

    kili_api_gateway.list_assets.assert_called_once_with(
        AssetFilters(project_id=ProjectId(project_id), asset_id_in=asset_ids),
        ["id", "jsonMetadata"],
        QueryOptions(disable_tqdm=True),
    )

    update_mock.assert_called_once()
    call_args = update_mock.call_args[1]

    assert call_args["asset_ids"] == asset_ids

    expected_metadata = [
        {"text": "Some text", "assetLabelingMetadata": {"new_key1": "new_value1"}},
        {
            "imageUrl": "http://example.com/image.jpg",
            "assetLabelingMetadata": {"new_key2": "new_value2"},
        },
    ]

    assert call_args["json_metadatas"] == expected_metadata
    assert result == [{"id": "asset1"}, {"id": "asset2"}]


def test_add_metadata_handles_missing_metadata(mocker: pytest_mock.MockerFixture):
    """Test that add_metadata can handle assets with no existing metadata."""
    kili_api_gateway = mocker.Mock(spec=KiliAPIGateway)

    existing_assets = [{"id": "asset1", "jsonMetadata": None}, {"id": "asset2", "jsonMetadata": {}}]

    kili_api_gateway.list_assets.return_value = existing_assets

    update_mock = mocker.patch.object(MutationsAsset, "update_properties_in_assets")
    update_mock.return_value = [{"id": "asset1"}, {"id": "asset2"}]

    mutations_asset = MutationsAsset()
    mutations_asset.kili_api_gateway = kili_api_gateway
    mutations_asset.graphql_client = mocker.Mock()

    project_id = "project1"
    asset_ids = ["asset1", "asset2"]
    new_metadata = [{"new_key1": "new_value1"}, {"new_key2": "new_value2"}]

    mutations_asset.add_metadata(
        asset_labeling_metadata=new_metadata, asset_ids=asset_ids, project_id=project_id
    )

    call_args = update_mock.call_args[1]

    expected_metadata = [
        {"assetLabelingMetadata": {"new_key1": "new_value1"}},
        {"assetLabelingMetadata": {"new_key2": "new_value2"}},
    ]

    assert call_args["json_metadatas"] == expected_metadata


def test_multiple_assets_with_different_metadata_structures(mocker: pytest_mock.MockerFixture):
    """Test that the functions handle multiple assets with different metadata structures."""
    kili_api_gateway = mocker.Mock(spec=KiliAPIGateway)

    existing_assets = [
        {"id": "asset1", "jsonMetadata": {"text": "Text 1"}},
        {
            "id": "asset2",
            "jsonMetadata": {
                "imageUrl": "http://example.com/image.jpg",
                "assetLabelingMetadata": {},
            },
        },
        {"id": "asset3", "jsonMetadata": None},
        {"id": "asset4", "jsonMetadata": {"assetLabelingMetadata": {"existing4": "value4"}}},
    ]

    kili_api_gateway.list_assets.return_value = existing_assets

    update_mock = mocker.patch.object(MutationsAsset, "update_properties_in_assets")
    update_mock.return_value = [{"id": f"asset{i}"} for i in range(1, 5)]

    mutations_asset = MutationsAsset()
    mutations_asset.kili_api_gateway = kili_api_gateway
    mutations_asset.graphql_client = mocker.Mock()

    project_id = "project1"
    asset_ids = ["asset1", "asset2", "asset3", "asset4"]
    new_metadata = [
        {"meta1": "value1"},
        {"meta2": "value2"},
        {"meta3": "value3"},
        {"meta4": "value4"},
    ]

    mutations_asset.add_metadata(
        asset_labeling_metadata=new_metadata, asset_ids=asset_ids, project_id=project_id
    )

    add_metadata_call_args = update_mock.call_args[1]

    update_mock.reset_mock()

    mutations_asset.set_metadata(
        asset_labeling_metadata=new_metadata, asset_ids=asset_ids, project_id=project_id
    )

    set_metadata_call_args = update_mock.call_args[1]

    expected_add_metadata = [
        {"text": "Text 1", "assetLabelingMetadata": {"meta1": "value1"}},
        {"imageUrl": "http://example.com/image.jpg", "assetLabelingMetadata": {"meta2": "value2"}},
        {"assetLabelingMetadata": {"meta3": "value3"}},
        {"assetLabelingMetadata": {"existing4": "value4", "meta4": "value4"}},
    ]

    expected_set_metadata = [
        {"text": "Text 1", "assetLabelingMetadata": {"meta1": "value1"}},
        {"imageUrl": "http://example.com/image.jpg", "assetLabelingMetadata": {"meta2": "value2"}},
        {"assetLabelingMetadata": {"meta3": "value3"}},
        {"assetLabelingMetadata": {"meta4": "value4"}},
    ]

    assert add_metadata_call_args["json_metadatas"] == expected_add_metadata
    assert set_metadata_call_args["json_metadatas"] == expected_set_metadata
