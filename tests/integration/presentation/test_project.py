import pytest
import pytest_mock

from kili.adapters.http_client import HttpClient
from kili.adapters.kili_api_gateway.helpers.queries import fragment_builder
from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.adapters.kili_api_gateway.project.operations import (
    GQL_COUNT_PROJECTS,
    GQL_CREATE_PROJECT,
    get_update_properties_in_project_mutation,
)
from kili.core.graphql.graphql_client import GraphQLClient
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


@pytest.fixture()
def kili_with_mocked_gateway(
    graphql_client: GraphQLClient, http_client: HttpClient
) -> ProjectClientMethods:
    kili = ProjectClientMethods()
    kili.kili_api_gateway = KiliAPIGateway(graphql_client=graphql_client, http_client=http_client)
    return kili


def test_when_counting_projects_of_an_author_then_the_author_is_in_the_where(
    kili_with_mocked_gateway: ProjectClientMethods, graphql_client: GraphQLClient
):
    graphql_client.execute.return_value = {"data": 0}

    # When
    count = kili_with_mocked_gateway.count_projects(author_id="colleague_id", archived=False)

    # Then
    assert count == 0
    query, variables = graphql_client.execute.call_args.args
    assert query == GQL_COUNT_PROJECTS
    assert variables["where"]["authorId"] == "colleague_id"
    assert variables["where"]["archived"] is False


def test_when_counting_projects_without_author_then_the_where_has_no_author_key(
    kili_with_mocked_gateway: ProjectClientMethods, graphql_client: GraphQLClient
):
    graphql_client.execute.return_value = {"data": 3}

    # When
    kili_with_mocked_gateway.count_projects()

    # Then an older Kili server, which does not know `authorId`, still accepts the call
    assert "authorId" not in graphql_client.execute.call_args.args[1]["where"]


def test_when_listing_projects_of_an_author_then_the_author_is_in_the_where(
    kili_with_mocked_gateway: ProjectClientMethods, mocker: pytest_mock.MockerFixture
):
    mocked_list = mocker.patch.object(
        kili_with_mocked_gateway.kili_api_gateway, "list_projects", return_value=iter([])
    )

    # When
    projects = kili_with_mocked_gateway.projects(
        author_id="colleague_id", fields=["id"], disable_tqdm=True
    )

    # Then
    assert projects == []
    assert mocked_list.call_args.args[0].author_id == "colleague_id"


def test_when_transferring_a_project_then_the_mutation_sets_and_asks_for_the_author_id(
    kili_with_mocked_gateway: ProjectClientMethods,
    graphql_client: GraphQLClient,
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch.object(
        kili_with_mocked_gateway.kili_api_gateway,
        "list_projects",
        return_value=iter([{"id": "p1"}]),
    )
    graphql_client.execute.return_value = {"data": {"id": "p1", "author": {"id": "new_author_id"}}}

    # When
    outcome = kili_with_mocked_gateway.transfer_projects_authorship(
        "former_author_id", "new_author_id"
    )

    # Then
    assert outcome == {"transferred": ["p1"], "failed": []}
    mutation, variables = graphql_client.execute.call_args.args
    assert mutation == get_update_properties_in_project_mutation(
        fragment_builder(["author.id", "id"])
    )
    assert "author{ id}" in mutation
    assert variables["where"] == {"id": "p1"}
    assert variables["data"]["author"] == "new_author_id"


def test_when_listing_and_counting_projects_of_an_email_then_the_email_is_in_the_where(
    kili_with_mocked_gateway: ProjectClientMethods,
    graphql_client: GraphQLClient,
    mocker: pytest_mock.MockerFixture,
):
    mocked_list = mocker.patch.object(
        kili_with_mocked_gateway.kili_api_gateway, "list_projects", return_value=iter([])
    )
    graphql_client.execute.return_value = {"data": 0}

    # When
    kili_with_mocked_gateway.projects(
        author_email="Jane@Acme.com", fields=["id"], disable_tqdm=True
    )
    kili_with_mocked_gateway.count_projects(author_email="Jane@Acme.com")

    # Then the address goes to the server as it was written, and not as an id
    assert mocked_list.call_args.args[0].author_email == "Jane@Acme.com"
    where = graphql_client.execute.call_args.args[1]["where"]
    assert where["authorEmail"] == "Jane@Acme.com"
    assert "authorId" not in where


def test_when_counting_projects_without_author_email_then_the_where_has_no_such_key(
    kili_with_mocked_gateway: ProjectClientMethods, graphql_client: GraphQLClient
):
    graphql_client.execute.return_value = {"data": 3}

    # When
    kili_with_mocked_gateway.count_projects()

    # Then an older Kili server, which does not know `authorEmail`, still accepts the call
    assert "authorEmail" not in graphql_client.execute.call_args.args[1]["where"]


def test_when_giving_an_id_and_an_email_for_the_author_then_it_is_refused(
    kili_with_mocked_gateway: ProjectClientMethods, graphql_client: GraphQLClient
):
    # Given an id and an email for the same author
    # When the projects are counted
    with pytest.raises(ValueError, match="not both"):
        kili_with_mocked_gateway.count_projects(author_id="user_id", author_email="a@acme.com")

    # Then it is refused before any call
    graphql_client.execute.assert_not_called()
