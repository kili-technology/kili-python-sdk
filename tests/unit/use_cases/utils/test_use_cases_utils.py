import pytest

from kili.adapters.kili_api_gateway import KiliAPIGateway
from kili.use_cases.utils.use_cases_utils import UseCasesUtils
from tests.fakes.fake_kili import mocked_AssetQuery, mocked_AssetQuery_count


@pytest.mark.parametrize(
    ("name", "asset_count"),
    (
        ("Given 150 external ids, the id <-> external_id mapping is correct", 150),
        ("Given 2400 external ids, the id <-> external_id mapping is correct", 2400),
    ),
)
def test__build_id_map_when_project_has_less_than_2000_assets(
    mocker, name, asset_count, graphql_client, http_client
):
    _ = name
    kili_api_gateway = mocker.MagicMock(spec=KiliAPIGateway)
    kili_api_gateway.graphql_client = graphql_client
    kili_api_gateway.http_client = http_client
    kili_api_gateway.list_assets.side_effect = mocked_AssetQuery
    kili_api_gateway.count_assets = mocker.MagicMock(side_effect=mocked_AssetQuery_count)

    asset_external_ids = [f"ext-{i}" for i in range(asset_count)]
    project_id = "object_detection_2500_assets"
    id_map = UseCasesUtils(kili_api_gateway)._build_id_map(asset_external_ids, project_id)

    assert id_map == {f"ext-{i}": f"{i}" for i in range(asset_count)}
