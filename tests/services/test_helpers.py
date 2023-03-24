import pytest

from kili.graphql.operations.asset.queries import AssetQuery
from kili.graphql.operations.project.queries import ProjectQuery
from kili.services.helpers import _build_id_map
from tests.fakes.fake_kili import (
    FakeAuth,
    mocked_AssetQuery,
    mocked_AssetQuery_count,
    mocked_ProjectQuery,
)


@pytest.mark.parametrize(
    "name,asset_count",
    (
        ("Given 150 external ids, the id <-> external_id mapping is correct", 150),
        ("Given 2400 external ids, the id <-> external_id mapping is correct", 2400),
    ),
)
def test__build_id_map_when_project_has_less_than_2000_assets(mocker, name, asset_count):
    _ = name
    auth = FakeAuth()
    mocker.patch.object(ProjectQuery, "__call__", side_effect=mocked_ProjectQuery)
    mocker.patch.object(AssetQuery, "__call__", side_effect=mocked_AssetQuery)
    mocker.patch.object(AssetQuery, "count", side_effect=mocked_AssetQuery_count)

    asset_external_ids = [f"ext-{i}" for i in range(asset_count)]
    project_id = "object_detection_2500_assets"
    id_map = _build_id_map(auth, asset_external_ids, project_id)

    assert id_map == {f"ext-{i}": f"{i}" for i in range(asset_count)}
