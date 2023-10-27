from kili.adapters.http_client import HttpClient
from kili.adapters.kili_api_gateway import KiliAPIGateway
from kili.adapters.kili_api_gateway.project.operations import get_projects_query
from kili.core.graphql.graphql_client import GraphQLClient
from kili.domain.project import ProjectId


def test_given_project_id_when_i_query_it_it_works(
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
