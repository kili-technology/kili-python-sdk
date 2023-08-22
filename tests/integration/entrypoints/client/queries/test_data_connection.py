import pytest

from kili.entrypoints.queries.data_connection import QueriesDataConnection


def test_data_connections(mocker):
    """Test data_connections query."""
    kili = QueriesDataConnection()
    kili.graphql_client = mocker.MagicMock()
    kili.http_client = mocker.MagicMock()
    kili.cloud_storage_connections(project_id="789465123")
    kili.graphql_client.execute.assert_called_once()
    query_sent = kili.graphql_client.execute.call_args[0][0]
    variables = kili.graphql_client.execute.call_args[0][1]

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


def test_data_connection(mocker):
    """Test data_connection query."""
    kili = QueriesDataConnection()
    kili.graphql_client = mocker.MagicMock()
    kili.http_client = mocker.MagicMock()
    with pytest.raises(ValueError, match="No data connection with id my_data_connection_id"):
        kili.cloud_storage_connections(
            cloud_storage_connection_id="my_data_connection_id", fields=["my_field"]
        )

    kili.graphql_client.execute.assert_called_once()
    query_sent = kili.graphql_client.execute.call_args[0][0]
    variables = kili.graphql_client.execute.call_args[0][1]

    assert "query dataConnection($where: DataConnectionIdWhere!)" in query_sent
    assert "data: dataConnection(where: $where)" in query_sent
    assert "my_field" in query_sent

    assert variables == {"where": {"id": "my_data_connection_id"}, "first": 1, "skip": 0}
