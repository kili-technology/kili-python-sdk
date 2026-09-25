import pytest_mock

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.domain.asset import AssetExternalId, AssetId
from kili.domain.project import ProjectId
from kili.presentation.client.asset import AssetClientMethods


def test_deleted_assets_lists_the_restorable_assets_with_their_deletion_date(
    mocker: pytest_mock.MockerFixture, kili_api_gateway: KiliAPIGateway
):
    # Given
    kili = AssetClientMethods()
    kili.kili_api_gateway = kili_api_gateway
    deleted = [{"id": "a1", "externalId": "img1", "deletedAt": "2026-09-24T09:12:43.921Z"}]
    list_deleted = mocker.patch(
        "kili.presentation.client.asset.AssetUseCases.list_deleted_assets",
        return_value=iter(deleted),
    )

    # When
    assets = kili.deleted_assets(project_id="project_id", first=5, disable_tqdm=True)

    # Then
    assert assets == deleted
    list_deleted.assert_called_once_with(
        ProjectId("project_id"),
        ("id", "externalId", "deletedAt"),
        QueryOptions(disable_tqdm=True, first=5, skip=0),
    )


def test_deleted_assets_as_generator(
    mocker: pytest_mock.MockerFixture, kili_api_gateway: KiliAPIGateway
):
    kili = AssetClientMethods()
    kili.kili_api_gateway = kili_api_gateway
    mocker.patch(
        "kili.presentation.client.asset.AssetUseCases.list_deleted_assets",
        return_value=iter([{"id": "a1"}]),
    )

    assets = kili.deleted_assets(project_id="project_id", fields=["id"], as_generator=True)

    assert not isinstance(assets, list)
    assert list(assets) == [{"id": "a1"}]


def test_count_deleted_assets(mocker: pytest_mock.MockerFixture, kili_api_gateway: KiliAPIGateway):
    kili = AssetClientMethods()
    kili.kili_api_gateway = kili_api_gateway
    count = mocker.patch(
        "kili.presentation.client.asset.AssetUseCases.count_deleted_assets", return_value=2
    )

    assert kili.count_deleted_assets(project_id="project_id") == 2
    count.assert_called_once_with(ProjectId("project_id"))


def test_restore_assets_by_ids_or_external_ids(
    mocker: pytest_mock.MockerFixture, kili_api_gateway: KiliAPIGateway
):
    kili = AssetClientMethods()
    kili.kili_api_gateway = kili_api_gateway
    restore = mocker.patch(
        "kili.presentation.client.asset.AssetUseCases.restore_assets",
        return_value=[{"id": "a1", "externalId": "img1"}],
    )

    assert kili.restore_assets(project_id="project_id", asset_ids=["a1"]) == [
        {"id": "a1", "externalId": "img1"}
    ]
    kili.restore_assets(project_id="project_id", external_ids=["img1"])

    assert restore.call_args_list == [
        mocker.call(ProjectId("project_id"), asset_ids=[AssetId("a1")], external_ids=None),
        mocker.call(
            ProjectId("project_id"), asset_ids=None, external_ids=[AssetExternalId("img1")]
        ),
    ]
