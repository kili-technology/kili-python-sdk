"""
Test module for the GraphQL client
"""
import os
from pathlib import Path
from unittest import mock

import pytest

from kili.client import Kili
from kili.exceptions import GraphQLError, TransportQueryError
from kili.graphql.graphql_client import GraphQLClient, GraphQLClientName


@pytest.mark.parametrize(
    "query",
    [
        "query MyQuery { my_query_is_clearly_not_valid_according_to_the_kili_schema { id } }",
        "query { projects { this_field_does_not_exist } }",
    ],
)
def test_gql_bad_query_local_validation(query):
    """test gql validation against local schema"""
    kili = Kili()  # fetch schema from kili server

    mocked_transport_execute = mock.MagicMock()
    kili.auth.client._gql_client.transport.execute = mocked_transport_execute  # type: ignore

    with pytest.raises(GraphQLError):
        kili.auth.client.execute(query)

    mocked_transport_execute.assert_not_called()


def test_gql_bad_query_remote_validation():
    """test validation by the server no local schema"""
    kili = Kili()

    query = """
    query MyQuery {
        my_query_is_clearly_not_valid_according_to_the_kili_schema {
            id
        }
    }
    """

    kili.auth.client._gql_client.schema = None
    kili.auth.client._gql_client.fetch_schema_from_transport = False
    mocked_validate = mock.MagicMock()
    kili.auth.client._gql_client.validate = mocked_validate

    with pytest.raises(TransportQueryError, match="Cannot query field"):
        kili.auth.client.execute(query)

    mocked_validate.assert_not_called()


SCHEMA_PATH = Path.home() / ".cache" / "kili" / "graphql" / "schema.graphql"


@mock.patch.object(GraphQLClient, "_get_graphql_schema_path", return_value=SCHEMA_PATH)
def test_graphql_client_cache(*_):
    api_endpoint = os.getenv("KILI_API_ENDPOINT")
    api_key = os.getenv("KILI_API_KEY")

    if SCHEMA_PATH.is_file():
        SCHEMA_PATH.unlink()

    _ = GraphQLClient(
        endpoint=api_endpoint,  # type: ignore
        api_key=api_key,  # type: ignore
        client_name=GraphQLClientName.SDK,
        verify=True,
    )
    assert SCHEMA_PATH.is_file()  # schema cached
    assert SCHEMA_PATH.stat().st_size > 0  # schema not empty

    with mock.patch("kili.graphql.graphql_client.print_schema") as mocked_print_schema:
        _ = GraphQLClient(
            endpoint=api_endpoint,  # type: ignore
            api_key=api_key,  # type: ignore
            client_name=GraphQLClientName.SDK,
            verify=True,
        )
        mocked_print_schema.assert_not_called()

    if SCHEMA_PATH.is_file():
        SCHEMA_PATH.unlink()


@mock.patch.object(GraphQLClient, "_get_kili_app_version", side_effect=Exception)
def test_graphql_client_cache_cant_get_kili_version(*_):
    """test when we can't get the kili version from the backend"""
    api_endpoint = os.getenv("KILI_API_ENDPOINT")
    api_key = os.getenv("KILI_API_KEY")

    _ = GraphQLClient(
        endpoint=api_endpoint,  # type: ignore
        api_key=api_key,  # type: ignore
        client_name=GraphQLClientName.SDK,
        verify=True,
    )
