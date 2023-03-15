"""
Test module for the GraphQL client
"""
import os
from pathlib import Path
from unittest import mock

import graphql
import pytest
from gql.transport import exceptions
from graphql import build_ast_schema, parse

from kili.client import Kili
from kili.exceptions import GraphQLError
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

    with pytest.raises(GraphQLError) as exc_info:
        kili.auth.client.execute(query)

    assert isinstance(exc_info.value.__cause__, graphql.GraphQLError)


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

    with pytest.raises(GraphQLError) as exc_info:
        kili.auth.client.execute(query)

    assert isinstance(exc_info.value.__cause__, exceptions.TransportQueryError)
    assert "Cannot query field" in str(exc_info.value.__cause__)

    mocked_validate.assert_not_called()


def test_graphql_client_cache(mocker):
    SCHEMA_PATH = Path.home() / ".cache" / "kili" / "graphql" / "schema.graphql"
    mocker.patch.object(GraphQLClient, "_get_graphql_schema_path", return_value=SCHEMA_PATH)

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


def test_outdated_cached_schema(mocker):
    """
    test when the schema in memory is outdated

    the client should refecth an up-to-date schema and retry the query automatically
    """
    SCHEMA_PATH = Path.home() / ".cache" / "kili" / "graphql" / "schema.graphql"
    mocker.patch.object(GraphQLClient, "_get_graphql_schema_path", return_value=SCHEMA_PATH)

    api_endpoint = os.getenv("KILI_API_ENDPOINT")
    api_key = os.getenv("KILI_API_KEY")

    # write a fake schema
    if SCHEMA_PATH.is_file():
        SCHEMA_PATH.unlink()

    fake_schema = """
    type Query {
        me: User
    }
    type User {
        id: ID
    }
    """
    SCHEMA_PATH.parent.mkdir(parents=True, exist_ok=True)
    SCHEMA_PATH.write_text(fake_schema)

    client = GraphQLClient(
        endpoint=api_endpoint,  # type: ignore
        api_key=api_key,  # type: ignore
        client_name=GraphQLClientName.SDK,
        verify=True,
    )

    client._gql_client.schema = build_ast_schema(parse(fake_schema))

    assert "email" not in client._gql_client.schema.type_map["User"].fields  # type: ignore

    # the query below will fail since the schema is outdated
    # but the client should fetch an up-to-date schema and retry
    result = client.execute("query MyQuery { me { email id } }")

    assert "email" in client._gql_client.schema.type_map["User"].fields  # type: ignore

    assert result["me"]["id"]  # pylint: disable=unsubscriptable-object
    assert result["me"]["email"]  # pylint: disable=unsubscriptable-object

    if SCHEMA_PATH.is_file():
        SCHEMA_PATH.unlink()
