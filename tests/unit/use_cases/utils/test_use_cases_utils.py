import pytest
import pytest_mock

from kili.adapters.kili_api_gateway.mixin import KiliAPIGateway
from kili.domain.asset import AssetExternalId
from kili.domain.project import ProjectId
from kili.use_cases.asset.utils import AssetUseCasesUtils
from tests.fakes.fake_kili import mocked_AssetQuery, mocked_AssetQuery_count


@pytest.mark.parametrize(
    ("name", "asset_count"),
    [
        ("Given 150 external ids, the id <-> external_id mapping is correct", 150),
        ("Given 2400 external ids, the id <-> external_id mapping is correct", 2400),
    ],
)
def test__build_id_map_when_project_has_less_than_2000_assets(
    mocker: pytest_mock.MockerFixture, name: str, asset_count: int, kili_api_gateway: KiliAPIGateway
):
    _ = name
    # Given
    kili_api_gateway.list_assets.side_effect = mocked_AssetQuery
    kili_api_gateway.count_assets = mocker.MagicMock(side_effect=mocked_AssetQuery_count)

    asset_external_ids = [AssetExternalId(f"ext-{i}") for i in range(asset_count)]
    project_id = ProjectId("object_detection_2500_assets")

    # When
    id_map = AssetUseCasesUtils(kili_api_gateway)._build_id_map(  # pylint: disable=protected-access
        asset_external_ids, project_id
    )

    # Then
    assert id_map == {f"ext-{i}": f"{i}" for i in range(asset_count)}
