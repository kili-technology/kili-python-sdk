from unittest.mock import MagicMock, patch

import pytest

from kili.queries.data_connection import QueriesDataConnection


@patch("kili.graphql.GraphQLClient")
def test_data_connections(mocked_graphql_client):
    """Test data_connections query."""
    kili = QueriesDataConnection(auth=MagicMock(client=mocked_graphql_client))
    kili.cloud_storage_connections(project_id="789465123")
    mocked_graphql_client.execute.assert_called_once()
    query_sent = mocked_graphql_client.execute.call_args[0][0]
    variables = mocked_graphql_client.execute.call_args[0][1]

    assert (
        "query dataConnections($where: DataConnectionsWhere!, $first: PageSize!, $skip: Int!)"
        in query_sent
    )
    assert "data: dataConnections(where: $where, first: $first, skip: $skip)" in query_sent
    assert "id lastChecked numberOfAssets selectedFolders projectId" in query_sent

    assert variables == {
        "where": {"integrationId": None, "projectId": "789465123"},
        "first": 100,
        "skip": 0,
    }


@patch("kili.graphql.GraphQLClient")
def test_data_connection(mocked_graphql_client):
    """Test data_connection query."""
    kili = QueriesDataConnection(auth=MagicMock(client=mocked_graphql_client))

    with pytest.raises(ValueError, match="No data connection with id my_data_connection_id"):
        kili.cloud_storage_connections(
            cloud_storage_connection_id="my_data_connection_id", fields=["my_field"]
        )

    mocked_graphql_client.execute.assert_called_once()
    query_sent = mocked_graphql_client.execute.call_args[0][0]
    variables = mocked_graphql_client.execute.call_args[0][1]

    assert "query dataConnection($where: DataConnectionIdWhere!)" in query_sent
    assert "data: dataConnection(where: $where)" in query_sent
    assert "my_field" in query_sent

    assert variables == {"where": {"id": "my_data_connection_id"}, "first": 1, "skip": 0}
