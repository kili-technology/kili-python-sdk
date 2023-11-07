import json
from typing import Dict

from kili.adapters.http_client import HttpClient
from kili.adapters.kili_api_gateway.helpers.queries import PaginatedGraphQLQuery
from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.adapters.kili_api_gateway.project.operations import get_projects_query
from kili.core.graphql.graphql_client import GraphQLClient
from kili.domain.project import ProjectFilters, ProjectId


def test_given_project_id_when_i_query_it_then_it_works(
    graphql_client: GraphQLClient, http_client: HttpClient
):
    graphql_client.execute.return_value = {
        "data": [{"id": "fake_project_id", "title": "fake_title"}]
    }
    # Given
    kili_gateway = KiliAPIGateway(graphql_client=graphql_client, http_client=http_client)

    # When
    project = kili_gateway.get_project(ProjectId("fake_project_id"), fields=("id", "title"))

    # Then
    assert project == {"id": "fake_project_id", "title": "fake_title"}
    graphql_client.execute.assert_called_once_with(
        query=get_projects_query(" id title"),
        variables={"where": {"id": "fake_project_id"}, "first": 1, "skip": 0},
    )


def test_given_projects_when_i_query_them_then_it_works(
    mocker, graphql_client: GraphQLClient, http_client: HttpClient
):
    mocker.patch.object(PaginatedGraphQLQuery, "get_number_of_elements_to_query", return_value=2)
    graphql_client.execute.return_value = {
        "data": [
            {"id": "fake_project_id_1", "jsonInterface": json.dumps({"jobs": {}})},
            {"id": "fake_project_id_2", "jsonInterface": json.dumps({"jobs": {}})},
        ]
    }

    # Given
    kili_gateway = KiliAPIGateway(graphql_client=graphql_client, http_client=http_client)

    # When
    projects = list(
        kili_gateway.list_projects(
            project_filters=ProjectFilters(id=None),
            fields=("id", "jsonInterface"),
            options=mocker.MagicMock(),
        )
    )

    # Then
    assert len(projects) == 2
    assert all(isinstance(proj["jsonInterface"], Dict) for proj in projects)
