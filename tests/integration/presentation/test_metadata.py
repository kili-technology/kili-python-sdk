"""Tests for asset metadata functions."""

from typing import Union, cast

import pytest
import pytest_mock

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.domain.asset import AssetExternalId, AssetFilters, AssetId
from kili.domain.project import ProjectId
from kili.entrypoints.mutations.asset import MutationsAsset
from kili.exceptions import IncompatibleArgumentsError, NotFound


def test_add_metadata_adds_to_existing_metadata(mocker: pytest_mock.MockerFixture):
    """Test that add_metadata adds new metadata without removing existing metadata."""
    kili_api_gateway = mocker.Mock(spec=KiliAPIGateway)

    existing_assets = [
        {
            "id": "asset1",
            "jsonMetadata": {"text": "Some text", "existing1": "value1"},
        },
        {
            "id": "asset2",
            "jsonMetadata": {"imageUrl": "http://example.com/image.jpg", "existing2": "value2"},
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
    new_metadata: list[dict[str, Union[str, float, int]]] = [
        {"new_key1": "new_value1"},
        {"new_key2": "new_value2"},
    ]

    result = mutations_asset.add_metadata(
        json_metadata=new_metadata, asset_ids=asset_ids, project_id=project_id
    )

    kili_api_gateway.list_assets.assert_called_once_with(
        AssetFilters(project_id=ProjectId(project_id), asset_id_in=cast(list[AssetId], asset_ids)),
        ["id", "jsonMetadata"],
        QueryOptions(disable_tqdm=True),
    )

    update_mock.assert_called_once()
    call_args = update_mock.call_args[1]

    assert call_args["asset_ids"] == asset_ids

    expected_metadata = [
        {"text": "Some text", "existing1": "value1", "new_key1": "new_value1"},
        {
            "imageUrl": "http://example.com/image.jpg",
            "existing2": "value2",
            "new_key2": "new_value2",
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
            "jsonMetadata": {"text": "Some text", "existing1": "value1", "should_be_removed": True},
        },
        {
            "id": "asset2",
            "jsonMetadata": {
                "imageUrl": "http://example.com/image.jpg",
                "existing2": "value2",
                "also_remove": "yes",
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
    new_metadata: list[dict[str, Union[str, float, int]]] = [
        {"new_key1": "new_value1"},
        {"new_key2": "new_value2"},
    ]

    result = mutations_asset.set_metadata(
        json_metadata=new_metadata, asset_ids=asset_ids, project_id=project_id
    )

    kili_api_gateway.list_assets.assert_called_once_with(
        AssetFilters(project_id=ProjectId(project_id), asset_id_in=cast(list[AssetId], asset_ids)),
        ["id", "jsonMetadata"],
        QueryOptions(disable_tqdm=True),
    )

    update_mock.assert_called_once()
    call_args = update_mock.call_args[1]

    assert call_args["asset_ids"] == asset_ids

    expected_metadata = [
        {"text": "Some text", "new_key1": "new_value1"},
        {"imageUrl": "http://example.com/image.jpg", "new_key2": "new_value2"},
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
    new_metadata: list[dict[str, Union[str, float, int]]] = [
        {"new_key1": "new_value1"},
        {"new_key2": "new_value2"},
    ]

    mutations_asset.add_metadata(
        json_metadata=new_metadata, asset_ids=asset_ids, project_id=project_id
    )

    call_args = update_mock.call_args[1]

    expected_metadata = [
        {"new_key1": "new_value1"},
        {"new_key2": "new_value2"},
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
            },
        },
        {"id": "asset3", "jsonMetadata": None},
        {"id": "asset4", "jsonMetadata": {"existing4": "value4"}},
    ]

    kili_api_gateway.list_assets.return_value = existing_assets

    update_mock = mocker.patch.object(MutationsAsset, "update_properties_in_assets")
    update_mock.return_value = [{"id": f"asset{i}"} for i in range(1, 5)]

    mutations_asset = MutationsAsset()
    mutations_asset.kili_api_gateway = kili_api_gateway
    mutations_asset.graphql_client = mocker.Mock()

    project_id = "project1"
    asset_ids = ["asset1", "asset2", "asset3", "asset4"]
    new_metadata: list[dict[str, Union[str, float, int]]] = [
        {"meta1": "value1"},
        {"meta2": "value2"},
        {"meta3": "value3"},
        {"meta4": "value4"},
    ]

    mutations_asset.add_metadata(
        json_metadata=new_metadata, asset_ids=asset_ids, project_id=project_id
    )

    add_metadata_call_args = update_mock.call_args[1]

    update_mock.reset_mock()

    mutations_asset.set_metadata(
        json_metadata=new_metadata, asset_ids=asset_ids, project_id=project_id
    )

    set_metadata_call_args = update_mock.call_args[1]

    expected_add_metadata = [
        {"text": "Text 1", "meta1": "value1"},
        {"imageUrl": "http://example.com/image.jpg", "meta2": "value2"},
        {"meta3": "value3"},
        {"existing4": "value4", "meta4": "value4"},
    ]

    expected_set_metadata = [
        {"text": "Text 1", "meta1": "value1"},
        {"imageUrl": "http://example.com/image.jpg", "meta2": "value2"},
        {"meta3": "value3"},
        {"meta4": "value4"},
    ]

    assert add_metadata_call_args["json_metadatas"] == expected_add_metadata
    assert set_metadata_call_args["json_metadatas"] == expected_set_metadata


def test_add_metadata_with_external_ids(mocker: pytest_mock.MockerFixture):
    """Test that add_metadata works correctly with external IDs."""
    kili_api_gateway = mocker.Mock(spec=KiliAPIGateway)

    existing_assets = [
        {
            "id": "asset1",
            "jsonMetadata": {"text": "Some text", "existing1": "value1"},
        },
        {
            "id": "asset2",
            "jsonMetadata": {"imageUrl": "http://example.com/image.jpg", "existing2": "value2"},
        },
    ]

    kili_api_gateway.list_assets.side_effect = [
        [{"id": "asset1", "externalId": "ext1"}, {"id": "asset2", "externalId": "ext2"}],
        existing_assets,
    ]

    update_mock = mocker.patch.object(MutationsAsset, "update_properties_in_assets")
    update_mock.return_value = [{"id": "asset1"}, {"id": "asset2"}]

    mutations_asset = MutationsAsset()
    mutations_asset.kili_api_gateway = kili_api_gateway
    mutations_asset.graphql_client = mocker.Mock()

    project_id = "project1"
    external_ids = ["ext1", "ext2"]
    new_metadata: list[dict[str, Union[str, float, int]]] = [
        {"new_key1": "new_value1"},
        {"new_key2": "new_value2"},
    ]

    result = mutations_asset.add_metadata(
        json_metadata=new_metadata, external_ids=external_ids, project_id=project_id
    )

    assert kili_api_gateway.list_assets.call_args_list == [
        mocker.call(
            AssetFilters(
                project_id=ProjectId(project_id),
                external_id_strictly_in=cast(list[AssetExternalId], external_ids),
            ),
            ["id", "externalId"],
            QueryOptions(disable_tqdm=True),
        ),
        mocker.call(
            AssetFilters(
                project_id=ProjectId(project_id),
                asset_id_in=cast(list[AssetId], ["asset1", "asset2"]),
            ),
            ["id", "jsonMetadata"],
            QueryOptions(disable_tqdm=True),
        ),
    ]

    update_mock.assert_called_once()
    call_args = update_mock.call_args[1]

    expected_metadata = [
        {"text": "Some text", "existing1": "value1", "new_key1": "new_value1"},
        {
            "imageUrl": "http://example.com/image.jpg",
            "existing2": "value2",
            "new_key2": "new_value2",
        },
    ]

    assert call_args["json_metadatas"] == expected_metadata
    assert result == [{"id": "asset1"}, {"id": "asset2"}]


def test_set_metadata_with_external_ids(mocker: pytest_mock.MockerFixture):
    """Test that set_metadata works correctly with external IDs."""
    kili_api_gateway = mocker.Mock(spec=KiliAPIGateway)

    existing_assets = [
        {
            "id": "asset1",
            "jsonMetadata": {"text": "Some text", "existing1": "value1", "should_be_removed": True},
        },
        {
            "id": "asset2",
            "jsonMetadata": {
                "imageUrl": "http://example.com/image.jpg",
                "existing2": "value2",
                "also_remove": "yes",
            },
        },
    ]

    kili_api_gateway.list_assets.side_effect = [
        [{"id": "asset1", "externalId": "ext1"}, {"id": "asset2", "externalId": "ext2"}],
        existing_assets,
    ]

    update_mock = mocker.patch.object(MutationsAsset, "update_properties_in_assets")
    update_mock.return_value = [{"id": "asset1"}, {"id": "asset2"}]

    mutations_asset = MutationsAsset()
    mutations_asset.kili_api_gateway = kili_api_gateway
    mutations_asset.graphql_client = mocker.Mock()

    project_id = "project1"
    external_ids = ["ext1", "ext2"]
    new_metadata: list[dict[str, Union[str, float, int]]] = [
        {"new_key1": "new_value1"},
        {"new_key2": "new_value2"},
    ]

    result = mutations_asset.set_metadata(
        json_metadata=new_metadata, external_ids=external_ids, project_id=project_id
    )

    assert kili_api_gateway.list_assets.call_args_list[0] == mocker.call(
        AssetFilters(
            project_id=ProjectId(project_id),
            external_id_strictly_in=cast(list[AssetExternalId], external_ids),
        ),
        ["id", "externalId"],
        QueryOptions(disable_tqdm=True),
    )

    update_mock.assert_called_once()
    call_args = update_mock.call_args[1]

    expected_metadata = [
        {"text": "Some text", "new_key1": "new_value1"},
        {"imageUrl": "http://example.com/image.jpg", "new_key2": "new_value2"},
    ]

    assert call_args["json_metadatas"] == expected_metadata
    assert result == [{"id": "asset1"}, {"id": "asset2"}]


def _mutations_asset(mocker: pytest_mock.MockerFixture, *list_assets_answers: list[dict]):
    """A MutationsAsset whose gateway answers each list_assets call in turn."""
    kili_api_gateway = mocker.Mock(spec=KiliAPIGateway)
    kili_api_gateway.list_assets.side_effect = list(list_assets_answers)
    update_mock = mocker.patch.object(MutationsAsset, "update_properties_in_assets")
    mutations_asset = MutationsAsset()
    mutations_asset.kili_api_gateway = kili_api_gateway
    mutations_asset.graphql_client = mocker.Mock()
    return mutations_asset, kili_api_gateway, update_mock


def test_add_metadata_puts_each_dict_on_the_asset_at_its_position(
    mocker: pytest_mock.MockerFixture,
):
    """Test that each dict lands on the asset given at its position, whatever order the API answers in."""
    # Given: the API answers in id order, the caller gives the ids the other way round
    mutations_asset, _, update_mock = _mutations_asset(
        mocker,
        [{"id": "a", "jsonMetadata": {"who": "nobody"}}, {"id": "b", "jsonMetadata": {}}],
    )

    # When
    mutations_asset.add_metadata(
        json_metadata=[{"who": "for_b"}, {"who": "for_a"}],
        project_id="project1",
        asset_ids=["b", "a"],
    )

    # Then
    assert update_mock.call_args[1] == {
        "asset_ids": ["b", "a"],
        "json_metadatas": [{"who": "for_b"}, {"who": "for_a"}],
    }


def test_set_metadata_puts_each_dict_on_the_asset_at_its_position_by_external_id(
    mocker: pytest_mock.MockerFixture,
):
    """Test that set_metadata matches external ids to their assets, not to the API's order."""
    mutations_asset, _, update_mock = _mutations_asset(
        mocker,
        [{"id": "a", "externalId": "x"}, {"id": "b", "externalId": "y"}],
        [{"id": "a", "jsonMetadata": {"text": "kept"}}, {"id": "b", "jsonMetadata": {"k": "v"}}],
    )

    mutations_asset.set_metadata(
        json_metadata=[{"who": "for_y"}, {"who": "for_x"}],
        project_id="project1",
        external_ids=["y", "x"],
    )

    assert update_mock.call_args[1] == {
        "asset_ids": ["b", "a"],
        "json_metadatas": [{"who": "for_y"}, {"text": "kept", "who": "for_x"}],
    }


def test_set_metadata_never_touches_an_asset_whose_external_id_only_starts_alike(
    mocker: pytest_mock.MockerFixture,
):
    """Test that external_ids=["img_1"] writes img_1 alone, even if img_10 comes back with it."""
    mutations_asset, kili_api_gateway, update_mock = _mutations_asset(
        mocker,
        [{"id": "a1", "externalId": "img_1"}, {"id": "a10", "externalId": "img_10"}],
        [{"id": "a1", "jsonMetadata": {"keep": "img_1"}}],
    )

    mutations_asset.set_metadata(
        json_metadata=[{"split": "val"}], project_id="project1", external_ids=["img_1"]
    )

    resolution_filters = kili_api_gateway.list_assets.call_args_list[0][0][0]
    assert resolution_filters.external_id_strictly_in == ["img_1"]
    assert resolution_filters.external_id_in is None
    assert update_mock.call_args[1] == {"asset_ids": ["a1"], "json_metadatas": [{"split": "val"}]}


def test_add_metadata_resolves_more_than_ten_external_ids(mocker: pytest_mock.MockerFixture):
    """Test that more than ten external ids are resolved exactly, with no partial-match limit."""
    external_ids = [f"ext-{i:02d}" for i in range(11)]
    mutations_asset, _, update_mock = _mutations_asset(
        mocker,
        [{"id": f"id-{i:02d}", "externalId": f"ext-{i:02d}"} for i in range(11)],
        [{"id": f"id-{i:02d}", "jsonMetadata": {}} for i in range(11)],
    )

    mutations_asset.add_metadata(
        json_metadata=[{"batch": "B"}] * 11, project_id="project1", external_ids=external_ids
    )

    assert update_mock.call_args[1]["asset_ids"] == [f"id-{i:02d}" for i in range(11)]


@pytest.mark.parametrize("method", ["add_metadata", "set_metadata"])
def test_metadata_raises_when_an_asset_id_is_not_found(
    mocker: pytest_mock.MockerFixture, method: str
):
    """Test that an unknown asset id raises and nothing is written."""
    mutations_asset, _, update_mock = _mutations_asset(
        mocker, [{"id": "asset1", "jsonMetadata": {}}]
    )

    with pytest.raises(NotFound, match="missing"):
        getattr(mutations_asset, method)(
            json_metadata=[{"x": "1"}, {"x": "2"}],
            project_id="project1",
            asset_ids=["asset1", "missing"],
        )

    update_mock.assert_not_called()


@pytest.mark.parametrize("method", ["add_metadata", "set_metadata"])
def test_metadata_raises_when_an_external_id_is_not_found(
    mocker: pytest_mock.MockerFixture, method: str
):
    """Test that an unknown external id raises and nothing is written."""
    mutations_asset, _, update_mock = _mutations_asset(
        mocker, [{"id": "asset1", "externalId": "ext1"}]
    )

    with pytest.raises(NotFound, match="no-such-asset"):
        getattr(mutations_asset, method)(
            json_metadata=[{"x": "1"}, {"x": "2"}],
            project_id="project1",
            external_ids=["ext1", "no-such-asset"],
        )

    update_mock.assert_not_called()


@pytest.mark.parametrize("method", ["add_metadata", "set_metadata"])
@pytest.mark.parametrize("asset_ids", [["asset1", "asset2"], []])
def test_metadata_raises_when_json_metadata_and_ids_differ_in_length(
    mocker: pytest_mock.MockerFixture, method: str, asset_ids: list[str]
):
    """Test that a metadata count other than the id count raises before anything is read."""
    mutations_asset, kili_api_gateway, update_mock = _mutations_asset(mocker)

    with pytest.raises(IncompatibleArgumentsError, match="one metadata dictionary per asset"):
        getattr(mutations_asset, method)(
            json_metadata=[{"split": "val"}], project_id="project1", asset_ids=asset_ids
        )

    kili_api_gateway.list_assets.assert_not_called()
    update_mock.assert_not_called()


def test_add_metadata_gives_an_asset_given_twice_both_dicts(mocker: pytest_mock.MockerFixture):
    """Test that an asset given twice gets both dicts, in order, in one update."""
    mutations_asset, _, update_mock = _mutations_asset(
        mocker, [{"id": "asset1", "jsonMetadata": {"k": "v"}}]
    )

    mutations_asset.add_metadata(
        json_metadata=[{"a": "1", "c": "1"}, {"b": "2", "c": "2"}],
        project_id="project1",
        asset_ids=["asset1", "asset1"],
    )

    assert update_mock.call_args[1] == {
        "asset_ids": ["asset1"],
        "json_metadatas": [{"k": "v", "a": "1", "b": "2", "c": "2"}],
    }


@pytest.mark.parametrize("method", ["add_metadata", "set_metadata"])
def test_metadata_raises_when_an_external_id_matches_several_assets(
    mocker: pytest_mock.MockerFixture, method: str
):
    """Test that an external id two assets share raises instead of writing one of them."""
    mutations_asset, kili_api_gateway, update_mock = _mutations_asset(
        mocker, [{"id": "first", "externalId": "dup"}, {"id": "second", "externalId": "dup"}]
    )

    with pytest.raises(NotFound, match="'dup'"):
        getattr(mutations_asset, method)(
            json_metadata=[{"split": "val"}], project_id="project1", external_ids=["dup"]
        )

    assert kili_api_gateway.list_assets.call_count == 1
    update_mock.assert_not_called()


def test_set_metadata_gives_an_asset_given_twice_both_dicts_in_turn(
    mocker: pytest_mock.MockerFixture,
):
    """Test that the second dict sets the asset as the first left it, as a second call would."""
    mutations_asset, _, update_mock = _mutations_asset(
        mocker, [{"id": "asset1", "jsonMetadata": {"text": "old", "k": "v"}}]
    )

    mutations_asset.set_metadata(
        json_metadata=[{"text": "new", "a": "1"}, {"b": "2"}],
        project_id="project1",
        asset_ids=["asset1", "asset1"],
    )

    assert update_mock.call_args[1] == {
        "asset_ids": ["asset1"],
        "json_metadatas": [{"text": "new", "b": "2"}],
    }


def test_add_metadata_accepts_nested_values(mocker: pytest_mock.MockerFixture):
    """Test that metadata values can be nested dicts and lists."""
    mutations_asset, _, update_mock = _mutations_asset(
        mocker, [{"id": "asset1", "jsonMetadata": {}}]
    )

    mutations_asset.add_metadata(
        json_metadata=[{"nested": {"a": [1, 2]}, "flag": True, "none": None}],
        project_id="project1",
        asset_ids=["asset1"],
    )

    assert update_mock.call_args[1]["json_metadatas"] == [
        {"nested": {"a": [1, 2]}, "flag": True, "none": None}
    ]


def test_remove_metadata_removes_only_the_given_keys(mocker: pytest_mock.MockerFixture):
    """Test that remove_metadata removes the given keys and keeps every other one."""
    mutations_asset, _, update_mock = _mutations_asset(
        mocker,
        [{"id": "asset1", "externalId": "ext1"}, {"id": "asset2", "externalId": "ext2"}],
        [
            {"id": "asset1", "jsonMetadata": {"split": "train", "source": "scanner", "text": "t"}},
            {"id": "asset2", "jsonMetadata": {"split": "val"}},
        ],
    )

    mutations_asset.remove_metadata(
        keys=["source", "text"], project_id="project1", external_ids=["ext2", "ext1"]
    )

    assert update_mock.call_args[1] == {
        "asset_ids": ["asset2", "asset1"],
        "json_metadatas": [{"split": "val"}, {"split": "train"}],
    }


def test_remove_metadata_refuses_processing_parameters(mocker: pytest_mock.MockerFixture):
    """Test that processingParameters, which Kili keeps, is refused instead of silently kept."""
    mutations_asset, kili_api_gateway, update_mock = _mutations_asset(mocker)

    with pytest.raises(ValueError, match="add_metadata"):
        mutations_asset.remove_metadata(
            keys=["processingParameters"], project_id="project1", asset_ids=["asset1"]
        )

    kili_api_gateway.list_assets.assert_not_called()
    update_mock.assert_not_called()


@pytest.mark.parametrize(
    ("keys", "asset_ids"),
    [([], ["asset1"]), (["source"], [])],
)
def test_remove_metadata_does_nothing_on_an_empty_list(
    mocker: pytest_mock.MockerFixture, keys: list[str], asset_ids: list[str]
):
    """Test that no key or no asset reads and writes nothing."""
    mutations_asset, kili_api_gateway, update_mock = _mutations_asset(mocker)

    with pytest.warns(UserWarning, match="did nothing"):
        assert (
            mutations_asset.remove_metadata(keys=keys, project_id="project1", asset_ids=asset_ids)
            == []
        )

    kili_api_gateway.list_assets.assert_not_called()
    update_mock.assert_not_called()
