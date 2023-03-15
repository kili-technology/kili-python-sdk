from kili.graphql.graphql_client import GraphQLClient, GraphQLClientName


def test_graphql_client_cache_cant_get_kili_version(mocker):
    """test when we can't get the kili version from the backend"""

    mocker.patch("kili.graphql.graphql_client.Client", return_value=None)
    mocker.patch.object(GraphQLClient, "_get_kili_app_version", return_value=None)

    _ = GraphQLClient(
        endpoint="https://",
        api_key="nokey",
        client_name=GraphQLClientName.SDK,
        verify=True,
    )
