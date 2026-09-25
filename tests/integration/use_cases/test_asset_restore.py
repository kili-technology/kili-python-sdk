"""Tests of the use cases listing, counting and restoring the deleted assets of a project."""

import pytest

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.domain.asset import AssetExternalId, AssetFilters, AssetId
from kili.domain.project import ProjectId
from kili.exceptions import GraphQLError, IncompatibleArgumentsError, MissingArgumentError, NotFound
from kili.use_cases.asset import AssetUseCases

PROJECT_ID = ProjectId("project_id")


def given_assets(kili_api_gateway: KiliAPIGateway, deleted: list[dict], active: list[dict]):
    """Answer list_assets like the backend: the deleted assets with showOnlyRestorable."""

    def list_assets(filters: AssetFilters, fields, options):
        assets = deleted if filters.show_only_restorable else active
        if filters.asset_id_in is not None:
            return iter([a for a in assets if a["id"] in filters.asset_id_in])
        if filters.external_id_strictly_in is not None:
            return iter([a for a in assets if a["externalId"] in filters.external_id_strictly_in])
        return iter(assets)

    kili_api_gateway.list_assets.side_effect = list_assets
    kili_api_gateway.restore_deleted_assets.side_effect = lambda project_id, asset_ids: list(
        asset_ids
    )


def restore_calls(kili_api_gateway: KiliAPIGateway) -> list[list[str]]:
    return [list(call.args[1]) for call in kili_api_gateway.restore_deleted_assets.call_args_list]


def test_list_deleted_assets_queries_the_restorable_assets_of_the_project(
    kili_api_gateway: KiliAPIGateway,
):
    kili_api_gateway.list_assets.return_value = iter([{"id": "a1"}])
    options = QueryOptions(disable_tqdm=True, first=10, skip=0)

    assets = list(AssetUseCases(kili_api_gateway).list_deleted_assets(PROJECT_ID, ("id",), options))

    assert assets == [{"id": "a1"}]
    kili_api_gateway.list_assets.assert_called_once_with(
        AssetFilters(project_id=PROJECT_ID, show_only_restorable=True), ("id",), options
    )


def test_count_deleted_assets_counts_the_restorable_assets_of_the_project(
    kili_api_gateway: KiliAPIGateway,
):
    kili_api_gateway.count_assets.return_value = 3

    assert AssetUseCases(kili_api_gateway).count_deleted_assets(PROJECT_ID) == 3
    kili_api_gateway.count_assets.assert_called_once_with(
        AssetFilters(project_id=PROJECT_ID, show_only_restorable=True)
    )


def test_restore_by_ids_checks_permission_then_restores_them_in_one_call(
    kili_api_gateway: KiliAPIGateway,
):
    deleted = [{"id": "a1", "externalId": "img1"}, {"id": "a2", "externalId": "img2"}]
    given_assets(kili_api_gateway, deleted=deleted, active=[{"id": "a3", "externalId": "img3"}])

    restored = AssetUseCases(kili_api_gateway).restore_assets(
        PROJECT_ID, asset_ids=[AssetId("a2"), AssetId("a1")], external_ids=None
    )

    assert restored == [{"id": "a2", "externalId": "img2"}, {"id": "a1", "externalId": "img1"}]
    assert restore_calls(kili_api_gateway) == [[], ["a2", "a1"]]


def test_restore_by_external_ids_resolves_them_among_the_deleted_assets(
    kili_api_gateway: KiliAPIGateway,
):
    deleted = [{"id": "a1", "externalId": "img1"}, {"id": "a2", "externalId": "img2"}]
    # an active asset whose external id is a substring of the deleted one: exact match only
    given_assets(kili_api_gateway, deleted=deleted, active=[{"id": "a9", "externalId": "img"}])

    restored = AssetUseCases(kili_api_gateway).restore_assets(
        PROJECT_ID, asset_ids=None, external_ids=[AssetExternalId("img1")]
    )

    assert restored == [{"id": "a1", "externalId": "img1"}]
    assert restore_calls(kili_api_gateway) == [[], ["a1"]]


def test_restore_returns_only_the_assets_the_backend_restored(kili_api_gateway: KiliAPIGateway):
    deleted = [{"id": "a1", "externalId": "img1"}, {"id": "a2", "externalId": "img2"}]
    given_assets(kili_api_gateway, deleted=deleted, active=[])
    # permanently deleted between the check and the restore
    kili_api_gateway.restore_deleted_assets.side_effect = lambda project_id, asset_ids: [
        AssetId(asset_id) for asset_id in asset_ids if asset_id == "a2"
    ]

    with pytest.warns(UserWarning, match=r"\['a1'\] were not reported as restored"):
        restored = AssetUseCases(kili_api_gateway).restore_assets(
            PROJECT_ID, asset_ids=[AssetId("a1"), AssetId("a2")], external_ids=None
        )

    assert restored == [{"id": "a2", "externalId": "img2"}]


def test_restore_of_an_asset_that_is_not_deleted_raises_not_found_and_restores_nothing(
    kili_api_gateway: KiliAPIGateway,
):
    given_assets(
        kili_api_gateway,
        deleted=[{"id": "a1", "externalId": "img1"}],
        active=[{"id": "a2", "externalId": "img2"}],
    )

    with pytest.raises(NotFound, match=r"\['a2'\].*Nothing was restored"):
        AssetUseCases(kili_api_gateway).restore_assets(
            PROJECT_ID, asset_ids=[AssetId("a1"), AssetId("a2")], external_ids=None
        )
    assert restore_calls(kili_api_gateway) == [[]]


def test_restore_of_an_unknown_external_id_raises_not_found_and_restores_nothing(
    kili_api_gateway: KiliAPIGateway,
):
    given_assets(kili_api_gateway, deleted=[{"id": "a1", "externalId": "img1"}], active=[])

    with pytest.raises(NotFound, match=r"\['unknown'\].*Nothing was restored"):
        AssetUseCases(kili_api_gateway).restore_assets(
            PROJECT_ID,
            asset_ids=None,
            external_ids=[AssetExternalId("img1"), AssetExternalId("unknown")],
        )
    assert restore_calls(kili_api_gateway) == [[]]


def test_restore_by_an_external_id_several_deleted_assets_have_asks_for_ids(
    kili_api_gateway: KiliAPIGateway,
):
    deleted = [{"id": "a1", "externalId": "img1"}, {"id": "a2", "externalId": "img1"}]
    given_assets(kili_api_gateway, deleted=deleted, active=[])

    with pytest.raises(ValueError, match=r"'img1': \['a1', 'a2'\].*asset id"):
        AssetUseCases(kili_api_gateway).restore_assets(
            PROJECT_ID, asset_ids=None, external_ids=[AssetExternalId("img1")]
        )
    assert restore_calls(kili_api_gateway) == [[]]


def test_restore_of_two_assets_sharing_an_external_id_raises_and_restores_nothing(
    kili_api_gateway: KiliAPIGateway,
):
    deleted = [{"id": "a1", "externalId": "img1"}, {"id": "a2", "externalId": "img1"}]
    given_assets(kili_api_gateway, deleted=deleted, active=[])

    with pytest.raises(ValueError, match=r"share external ids.*'img1'.*Nothing was restored"):
        AssetUseCases(kili_api_gateway).restore_assets(
            PROJECT_ID, asset_ids=[AssetId("a1"), AssetId("a2")], external_ids=None
        )
    assert restore_calls(kili_api_gateway) == [[]]


def test_restore_of_an_asset_whose_external_id_is_used_raises_and_restores_nothing(
    kili_api_gateway: KiliAPIGateway,
):
    deleted = [{"id": "a1", "externalId": "img1"}, {"id": "a2", "externalId": "img2"}]
    given_assets(kili_api_gateway, deleted=deleted, active=[{"id": "a3", "externalId": "img2"}])

    with pytest.raises(ValueError, match=r"\['img2'\] are already used.*'img2': 'a3'.*Nothing"):
        AssetUseCases(kili_api_gateway).restore_assets(
            PROJECT_ID, asset_ids=[AssetId("a1"), AssetId("a2")], external_ids=None
        )
    assert restore_calls(kili_api_gateway) == [[]]


def test_restore_of_assets_without_external_id_skips_the_external_id_checks(
    kili_api_gateway: KiliAPIGateway,
):
    deleted = [{"id": "a1", "externalId": ""}, {"id": "a2", "externalId": None}]
    given_assets(kili_api_gateway, deleted=deleted, active=[{"id": "a3", "externalId": ""}])

    restored = AssetUseCases(kili_api_gateway).restore_assets(
        PROJECT_ID, asset_ids=[AssetId("a1"), AssetId("a2")], external_ids=None
    )

    assert [asset["id"] for asset in restored] == ["a1", "a2"]


def test_restore_by_a_user_who_is_not_admin_raises_a_clear_error_and_restores_nothing(
    kili_api_gateway: KiliAPIGateway,
):
    given_assets(kili_api_gateway, deleted=[{"id": "a1", "externalId": "img1"}], active=[])
    kili_api_gateway.restore_deleted_assets.side_effect = GraphQLError(
        [{"message": "[accessDenied] Access denied."}]
    )

    with pytest.raises(GraphQLError, match="Only an admin of project project_id can restore"):
        AssetUseCases(kili_api_gateway).restore_assets(
            PROJECT_ID, asset_ids=[AssetId("a1")], external_ids=None
        )
    kili_api_gateway.list_assets.assert_not_called()
    assert restore_calls(kili_api_gateway) == [[]]


def test_restore_keeps_an_error_that_is_not_about_permissions(kili_api_gateway: KiliAPIGateway):
    error = GraphQLError([{"message": "[licenseError] Your license does not allow it."}])
    kili_api_gateway.restore_deleted_assets.side_effect = error

    with pytest.raises(GraphQLError) as raised:
        AssetUseCases(kili_api_gateway).restore_assets(
            PROJECT_ID, asset_ids=[AssetId("a1")], external_ids=None
        )
    assert raised.value is error


def test_restore_of_no_asset_restores_nothing(kili_api_gateway: KiliAPIGateway):
    given_assets(kili_api_gateway, deleted=[], active=[])

    assert AssetUseCases(kili_api_gateway).restore_assets(PROJECT_ID, [], None) == []
    assert restore_calls(kili_api_gateway) == [[]]


def test_restore_with_both_ids_and_external_ids_is_refused(kili_api_gateway: KiliAPIGateway):
    with pytest.raises(IncompatibleArgumentsError):
        AssetUseCases(kili_api_gateway).restore_assets(
            PROJECT_ID, asset_ids=[AssetId("a1")], external_ids=[AssetExternalId("img1")]
        )


def test_restore_without_ids_nor_external_ids_is_refused(kili_api_gateway: KiliAPIGateway):
    with pytest.raises(MissingArgumentError):
        AssetUseCases(kili_api_gateway).restore_assets(PROJECT_ID, None, None)
