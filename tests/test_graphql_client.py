from unittest import mock

from kili.graphql.graphql_client import GraphQLClient, GraphQLClientName


@mock.patch.object(GraphQLClient, "_get_kili_app_version", side_effect=Exception)
@mock.patch("kili.graphql.graphql_client.Client", return_value=None)
def test_graphql_client_cache_cant_get_kili_version(*_):
    """test when we can't get the kili version from the backend"""
    _ = GraphQLClient(
        endpoint="https://",
        api_key="nokey",
        client_name=GraphQLClientName.SDK,
        verify=True,
    )
