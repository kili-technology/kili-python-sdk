import os
from pathlib import Path
from tempfile import TemporaryDirectory
from time import time
from unittest import mock

import graphql
import pytest
import pytest_mock
from pyrate_limiter import Duration, Limiter, RequestRate

from kili.adapters.http_client import HttpClient
from kili.core.constants import MAX_CALLS_PER_MINUTE
from kili.core.graphql.graphql_client import GraphQLClient, GraphQLClientName
from kili.exceptions import GraphQLError


def test_graphql_client_cache_cant_get_kili_version(mocker):
    """Test when we can't get the kili version from the backend."""
    mocker.patch("kili.core.graphql.graphql_client.Client", return_value=None)
    mocker.patch.object(GraphQLClient, "_get_kili_app_version", return_value=None)

    _ = GraphQLClient(
        endpoint="https://",
        api_key="nokey",
        client_name=GraphQLClientName.SDK,
        verify=True,
        http_client=HttpClient(
            kili_endpoint="https://fake_endpoint.kili-technology.com", api_key="", verify=True
        ),
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
        http_client=HttpClient(
            kili_endpoint="https://fake_endpoint.kili-technology.com", api_key="", verify=True
        ),
    )

    with pytest.raises(GraphQLError) as exc_info:
        client.execute(query)

    assert isinstance(exc_info.value.__cause__, graphql.GraphQLError)


def test_graphql_client_cache(mocker):
    with TemporaryDirectory() as temp_dir:
        schema_path = Path(temp_dir) / "schema.graphql"
        mocker.patch.object(GraphQLClient, "_get_graphql_schema_path", return_value=schema_path)

        api_endpoint = os.getenv(
            "KILI_API_ENDPOINT", "https://cloud.kili-technology.com/api/label/v2/graphql"
        )

        # we need to remove "Authorization" api key from the header
        # if not, the backend will refuse the introspection query
        mocker.patch.object(GraphQLClient, "_get_headers", return_value={})

        # initialize a client with schema caching enabled
        _ = GraphQLClient(
            endpoint=api_endpoint,
            api_key="",
            client_name=GraphQLClientName.SDK,
            verify=True,
            http_client=HttpClient(
                kili_endpoint="https://fake_endpoint.kili-technology.com", api_key="", verify=True
            ),
            enable_schema_caching=True,
            graphql_schema_cache_dir=temp_dir,
        )

        # schema should be cached
        files_in_cache_dir = list(schema_path.parent.glob("*"))
        assert schema_path.is_file(), f"{files_in_cache_dir}, {schema_path}"
        assert schema_path.stat().st_size > 0

        # check that the schema is not fetched again when we initialize a new client
        with mock.patch("kili.core.graphql.graphql_client.print_schema") as mocked_print_schema:
            _ = GraphQLClient(
                endpoint=api_endpoint,
                api_key="",
                client_name=GraphQLClientName.SDK,
                verify=True,
                http_client=HttpClient(
                    kili_endpoint="https://fake_endpoint.kili-technology.com",
                    api_key="",
                    verify=True,
                ),
                enable_schema_caching=True,
                graphql_schema_cache_dir=temp_dir,
            )
            mocked_print_schema.assert_not_called()


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
            http_client=HttpClient(
                kili_endpoint="https://fake_endpoint.kili-technology.com", api_key="", verify=True
            ),
        )


def test_skip_checks_disable_local_validation(mocker: pytest_mock.MockerFixture):
    mocker_gql = mocker.patch("kili.core.graphql.graphql_client.Client", return_value=None)
    mocker.patch.dict(os.environ, {"KILI_SDK_SKIP_CHECKS": "true"})
    client = GraphQLClient(
        endpoint="",
        api_key="",
        client_name=GraphQLClientName.SDK,
        http_client=HttpClient(
            kili_endpoint="https://fake_endpoint.kili-technology.com", api_key="", verify=True
        ),
    )
    mocker_gql.assert_called_with(
        transport=client._gql_transport,
        fetch_schema_from_transport=False,
        introspection_args=client._get_introspection_args(),
    )


def test_rate_limiting(mocker: pytest_mock.MockerFixture):
    mocker.patch("kili.core.graphql.graphql_client.GraphQLClient._get_kili_app_version")
    mocker.patch("kili.core.graphql.graphql_client.gql", side_effect=lambda x: x)
    mocker.patch(
        "kili.core.graphql.graphql_client._limiter",
        new=Limiter(RequestRate(MAX_CALLS_PER_MINUTE, Duration.SECOND * 5)),
    )
    client = GraphQLClient(
        endpoint="",
        api_key="",
        client_name=GraphQLClientName.SDK,
        http_client=HttpClient(
            kili_endpoint="https://fake_endpoint.kili-technology.com", api_key="", verify=True
        ),
        enable_schema_caching=False,
    )

    last_call_timestamp = before_last_call_timestamp = 0

    def mock_execute(*args, **kwargs):
        nonlocal last_call_timestamp
        nonlocal before_last_call_timestamp
        before_last_call_timestamp = last_call_timestamp
        last_call_timestamp = time()

    client._gql_client = mocker.MagicMock()
    client._gql_client.execute.side_effect = mock_execute

    # first calls should not be rate limited
    for _ in range(MAX_CALLS_PER_MINUTE):
        client.execute(query="")

    # next calls should be rate limited
    client.execute(query="")

    # at least 1 second delay for the last call
    assert last_call_timestamp - before_last_call_timestamp > 1
