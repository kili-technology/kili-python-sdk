"""
Test module for the GraphQL client
"""
import os
from pathlib import Path
from unittest import mock

import pytest
from gql.transport import exceptions
from graphql import build_ast_schema, parse

from kili.exceptions import GraphQLError
from kili.graphql.graphql_client import GraphQLClient, GraphQLClientName


def test_gql_bad_query_remote_validation():
    """test validation by the server no local schema"""
    api_endpoint = os.getenv("KILI_API_ENDPOINT")
    api_key = os.getenv("KILI_API_KEY")

    client = GraphQLClient(
        endpoint=api_endpoint,  # type: ignore
        api_key=api_key,  # type: ignore
        client_name=GraphQLClientName.SDK,
        verify=True,
    )

    query = """
    query MyQuery {
        my_query_is_clearly_not_valid_according_to_the_kili_schema {
            id
        }
    }
    """

    client._gql_client.schema = None
    client._gql_client.fetch_schema_from_transport = False
    mocked_validate = mock.MagicMock()
    client._gql_client.validate = mocked_validate

    with pytest.raises(GraphQLError) as exc_info:
        client.execute(query)

    assert isinstance(exc_info.value.__cause__, exceptions.TransportQueryError)
    assert "Cannot query field" in str(exc_info.value.__cause__)

    mocked_validate.assert_not_called()


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
