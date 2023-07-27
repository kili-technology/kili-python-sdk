import os
from pathlib import Path
from unittest import mock

import graphql
import pytest
import pytest_mock
from gql.transport.exceptions import TransportServerError

from kili.core.graphql.graphql_client import GraphQLClient, GraphQLClientName
from kili.exceptions import GraphQLError


def test_graphql_client_cache_cant_get_kili_version(mocker):
    """Test when we can't get the kili version from the backend."""
    mocker.patch("kili.core.graphql.graphql_client.Client", return_value=None)

    _ = GraphQLClient(
        endpoint="https://",
        api_key="nokey",
        client_name=GraphQLClientName.SDK,
        verify=True,
        kili_app_version=None,
    )


@pytest.mark.parametrize(
    "query",
    [
        "query MyQuery { my_query_is_clearly_not_valid_according_to_the_kili_schema { id } }",
        "query { projects { this_field_does_not_exist } }",
    ],
)
def test_gql_bad_query_local_validation(query, mocker):
    """Test gql validation against local schema."""
    api_endpoint = os.getenv(
        "KILI_API_ENDPOINT", "https://cloud.kili-technology.com/api/label/v2/graphql"
    )

    # we need to remove "Authorization" api key from the header
    # if not, the backend will refuse the introspection query
    mocker.patch.object(GraphQLClient, "_get_headers", return_value={})

    client = GraphQLClient(
        endpoint=api_endpoint,
        api_key="",
        client_name=GraphQLClientName.SDK,
        verify=True,
        kili_app_version="2.129.0",
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
    mocker.patch.object(GraphQLClient, "_get_headers", return_value={})

    if SCHEMA_PATH.is_file():
        SCHEMA_PATH.unlink()

    _ = GraphQLClient(
        endpoint=api_endpoint,
        api_key="",
        client_name=GraphQLClientName.SDK,
        verify=True,
        kili_app_version="2.129.0",
    )

    # schema should be cached
    files_in_cache_dir = list(SCHEMA_PATH.parent.glob("*"))
    assert SCHEMA_PATH.is_file(), f"{files_in_cache_dir}, {SCHEMA_PATH}"
    assert SCHEMA_PATH.stat().st_size > 0

    with mock.patch("kili.core.graphql.graphql_client.print_schema") as mocked_print_schema:
        _ = GraphQLClient(
            endpoint=api_endpoint,
            api_key="",
            client_name=GraphQLClientName.SDK,
            verify=True,
            kili_app_version="2.129.0",
        )
        mocked_print_schema.assert_not_called()

    if SCHEMA_PATH.is_file():
        SCHEMA_PATH.unlink()


def test_schema_caching_requires_cache_dir():
    with pytest.raises(
        Exception, match="must specify a cache directory if you want to enable schema caching"
    ):
        _ = GraphQLClient(
            endpoint="",
            api_key="",
            client_name=GraphQLClientName.SDK,
            enable_schema_caching=True,
            graphql_schema_cache_dir=None,
            kili_app_version="2.129.0",
        )


def test_skip_checks_disable_local_validation(mocker: pytest_mock.MockerFixture):
    mocker_gql = mocker.patch("kili.core.graphql.graphql_client.Client", return_value=None)
    mocker.patch.dict(os.environ, {"KILI_SDK_SKIP_CHECKS": "true"})
    client = GraphQLClient(
        endpoint="", api_key="", client_name=GraphQLClientName.SDK, kili_app_version="2.129.0"
    )
    mocker_gql.assert_called_with(
        transport=client._gql_transport,
        fetch_schema_from_transport=False,
        introspection_args=client._get_introspection_args(),
    )
