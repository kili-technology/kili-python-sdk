import os
from pathlib import Path
from unittest import mock

import graphql
import pytest

from kili.exceptions import GraphQLError
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


@pytest.mark.parametrize(
    "query",
    [
        "query MyQuery { my_query_is_clearly_not_valid_according_to_the_kili_schema { id } }",
        "query { projects { this_field_does_not_exist } }",
    ],
)
def test_gql_bad_query_local_validation(query, mocker):
    """test gql validation against local schema"""
    api_endpoint = os.getenv(
        "KILI_API_ENDPOINT", "https://cloud.kili-technology.com/api/label/v2/graphql"
    )

    # we need to remove "Authorization" api key from the header
    # if not, the backend will refuse the introspection query
    mocker.patch.object(GraphQLClient, "headers", return_value={})

    client = GraphQLClient(
        endpoint=api_endpoint,
        api_key="",
        client_name=GraphQLClientName.SDK,
        verify=True,
    )

    with pytest.raises(GraphQLError) as exc_info:
        client.execute(query)

    assert isinstance(exc_info.value.__cause__, graphql.GraphQLError)


def test_graphql_client_cache(mocker):
    SCHEMA_PATH = Path.home() / ".cache" / "kili" / "graphql" / "schema.graphql"
    mocker.patch.object(GraphQLClient, "_get_graphql_schema_path", return_value=SCHEMA_PATH)

    api_endpoint = os.getenv(
        "KILI_API_ENDPOINT", "https://cloud.kili-technology.com/api/label/v2/graphql"
    )

    # we need to remove "Authorization" api key from the header
    # if not, the backend will refuse the introspection query
    mocker.patch.object(GraphQLClient, "headers", return_value={})

    if SCHEMA_PATH.is_file():
        SCHEMA_PATH.unlink()

    _ = GraphQLClient(
        endpoint=api_endpoint,
        api_key="",
        client_name=GraphQLClientName.SDK,
        verify=True,
    )
    assert SCHEMA_PATH.is_file()  # schema cached
    assert SCHEMA_PATH.stat().st_size > 0  # schema not empty

    with mock.patch("kili.graphql.graphql_client.print_schema") as mocked_print_schema:
        _ = GraphQLClient(
            endpoint=api_endpoint,
            api_key="",
            client_name=GraphQLClientName.SDK,
            verify=True,
        )
        mocked_print_schema.assert_not_called()

    if SCHEMA_PATH.is_file():
        SCHEMA_PATH.unlink()
