import pytest_mock

from kili.adapters.kili_api_gateway.helpers.queries import fragment_builder
from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.adapters.kili_api_gateway.project.operations import (
    GQL_COUNT_PROJECTS,
    GQL_CREATE_PROJECT,
    get_update_properties_in_project_mutation,
)
from kili.presentation.client.project import ProjectClientMethods


def test_when_creating_project_then_it_returns_project_id(mocker: pytest_mock.MockerFixture):
    kili = ProjectClientMethods()
    kili.kili_api_gateway = KiliAPIGateway(
        graphql_client=mocker.MagicMock(), http_client=mocker.MagicMock()
    )
    kili.kili_api_gateway.get_project = mocker.MagicMock(return_value="fake_project_id")

    # When
    kili.create_project(input_type="IMAGE", json_interface={}, title="fake_title")

    # Then
    kili.kili_api_gateway.graphql_client.execute.assert_called_once_with(
        GQL_CREATE_PROJECT,
        {
            "data": {
                "description": "",
                "fromDemoProject": None,
                "inputType": "IMAGE",
                "jsonInterface": "{}",
                "title": "fake_title",
            }
        },
    )


def test_when_updating_project_then_it_returns_updated_project(mocker: pytest_mock.MockerFixture):
    kili = ProjectClientMethods()
    kili.kili_api_gateway = KiliAPIGateway(
        graphql_client=mocker.MagicMock(), http_client=mocker.MagicMock()
    )
    # Given
    project_id = "fake_proj_id"

    # When
    kili.update_properties_in_project(project_id, review_coverage=42)

    # Then
    kili.kili_api_gateway.graphql_client.execute.assert_called_once_with(
        get_update_properties_in_project_mutation(" reviewCoverage id"),
        {
            "where": {"id": "fake_proj_id"},
            "data": {
                "archived": None,
                "author": None,
                "consensusMark": None,
                "consensusTotCoverage": None,
                "description": None,
                "canNavigateBetweenAssets": None,
                "canSkipAsset": None,
                "honeypotMark": None,
                "instructions": None,
                "jsonInterface": None,
                "minConsensusSize": None,
                "reviewCoverage": 42,
                "shouldAutoAssign": None,
                "shouldRelaunchKpiComputation": None,
                "title": None,
                "useHoneyPot": None,
            },
        },
    )


def _kili_with_mocked_gateway(mocker: pytest_mock.MockerFixture) -> ProjectClientMethods:
    kili = ProjectClientMethods()
    kili.kili_api_gateway = KiliAPIGateway(
        graphql_client=mocker.MagicMock(), http_client=mocker.MagicMock()
    )
    return kili


def test_when_counting_projects_of_an_author_then_the_author_is_in_the_where(
    mocker: pytest_mock.MockerFixture,
):
    kili = _kili_with_mocked_gateway(mocker)
    kili.kili_api_gateway.graphql_client.execute.return_value = {"data": 0}

    # When
    count = kili.count_projects(author_id="colleague_id", archived=False)

    # Then
    assert count == 0
    where = kili.kili_api_gateway.graphql_client.execute.call_args.args[1]["where"]
    assert where["authorId"] == "colleague_id"
    assert where["archived"] is False
    assert kili.kili_api_gateway.graphql_client.execute.call_args.args[0] == GQL_COUNT_PROJECTS


def test_when_counting_projects_without_author_then_the_where_has_no_author_key(
    mocker: pytest_mock.MockerFixture,
):
    kili = _kili_with_mocked_gateway(mocker)
    kili.kili_api_gateway.graphql_client.execute.return_value = {"data": 3}

    # When
    kili.count_projects()

    # Then an older Kili server, which does not know `authorId`, still accepts the call
    where = kili.kili_api_gateway.graphql_client.execute.call_args.args[1]["where"]
    assert "authorId" not in where


def test_when_listing_projects_of_an_author_then_the_author_is_in_the_where(
    mocker: pytest_mock.MockerFixture,
):
    kili = _kili_with_mocked_gateway(mocker)
    mocked_list = mocker.patch.object(kili.kili_api_gateway, "list_projects", return_value=iter([]))

    # When
    projects = kili.projects(author_id="colleague_id", fields=["id"], disable_tqdm=True)

    # Then
    assert projects == []
    assert mocked_list.call_args.args[0].author_id == "colleague_id"


def test_when_transferring_a_project_then_the_mutation_sets_and_asks_for_the_author_id(
    mocker: pytest_mock.MockerFixture,
):
    kili = _kili_with_mocked_gateway(mocker)
    mocker.patch.object(kili.kili_api_gateway, "list_projects", return_value=iter([{"id": "p1"}]))
    kili.kili_api_gateway.graphql_client.execute.return_value = {
        "data": {"id": "p1", "author": {"id": "new_author_id"}}
    }

    # When
    outcome = kili.transfer_projects_authorship("former_author_id", "new_author_id")

    # Then
    assert outcome == {"transferred": ["p1"], "failed": []}
    mutation, variables = kili.kili_api_gateway.graphql_client.execute.call_args.args
    assert mutation == get_update_properties_in_project_mutation(
        fragment_builder(["author.id", "id"])
    )
    assert "author{ id}" in mutation
    assert variables["where"] == {"id": "p1"}
    assert variables["data"]["author"] == "new_author_id"
