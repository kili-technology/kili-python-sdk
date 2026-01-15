import os
from time import time

import pytest
import pytest_mock
from gql import Client
from gql.transport import exceptions
from graphql import ExecutionResult
from pyrate_limiter import Duration, Rate
from pyrate_limiter.limiter import Limiter

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
        new=Limiter(Rate(MAX_CALLS_PER_MINUTE, Duration.SECOND * 5), max_delay=120 * 1000),
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
        return ExecutionResult({"data": 1}, extensions=None)

    client._gql_client = mocker.MagicMock()
    client._gql_client.execute.side_effect = mock_execute
    client._gql_client.transport.response_headers = {}

    # first calls should not be rate limited
    for _ in range(MAX_CALLS_PER_MINUTE):
        client.execute(query="")

    # next calls should be rate limited
    client.execute(query="")

    # at least 1 second delay for the last call
    assert last_call_timestamp - before_last_call_timestamp > 1


def test_given_gql_client_when_the_server_refuses_wrong_query_then_it_does_no_retry(
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch("kili.core.graphql.graphql_client.gql", side_effect=lambda x: x)

    nb_times_called = 0

    def mocked_backend_response(*args, **kwargs):
        nonlocal nb_times_called
        nb_times_called += 1
        raise exceptions.TransportQueryError(
            msg=(
                "{'message': 'Variable \"$skip\" of required type \"Int!\" was not provided.',"
                " 'locations': [{'line': 1, 'column': 58}], 'extensions': {'code':"
                " 'INTERNAL_SERVER_ERROR'}}"
            ),
            errors=[
                {
                    "message": 'Variable "$skip" of required type "Int!" was not provided.',
                    "locations": [{"line": 1, "column": 58}],
                    "extensions": {"code": "INTERNAL_SERVER_ERROR"},
                }
            ],
            data=None,
            extensions=None,
        )

    mocked_execute = mocker.patch.object(Client, "execute", side_effect=mocked_backend_response)

    # Given
    client = GraphQLClient(
        endpoint="",
        api_key="",
        client_name=GraphQLClientName.SDK,
        http_client=HttpClient(
            kili_endpoint="https://fake_endpoint.kili-technology.com", api_key="", verify=True
        ),
        enable_schema_caching=False,
    )

    with pytest.raises(
        GraphQLError, match=r'Variable "(\$\w+)" of required type "(\w+!)" was not provided.'
    ):
        client.execute(query="fake_query")  # When

    assert mocked_execute.call_count == nb_times_called == 1


def test_given_gql_client_when_the_server_returns_flagsmith_error_then_it_retries(
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch("kili.core.graphql.graphql_client.gql", side_effect=lambda x: x)

    nb_times_called = 0

    def mocked_backend_response(*args, **kwargs):
        nonlocal nb_times_called
        nb_times_called += 1
        if nb_times_called > 2:
            return ExecutionResult({"data": "all good"}, extensions=None)
        raise exceptions.TransportQueryError(
            msg=(
                "[unexpectedRetrieving] Unexpected error when retrieving runtime information."
                " Please contact our support team if it occurs again. -- This can be due to:"
                " Invalid request made to Flagsmith API. Response status code: 502 | trace : Error:"
                " Invalid request made to Flagsmith API. Response status code: 502\n    at new"
                " FlagsmithAPIError"
                " (/snapshot/app/node_modules/flagsmith-nodejs/build/sdk/errors.js:30:42)\n    at"
                " Flagsmith.<anonymous>"
                " (/snapshot/app/node_modules/flagsmith-nodejs/build/sdk/index.js:373:35)\n    at"
                " step (/snapshot/app/node_modules/flagsmith-nodejs/build/sdk/index.js:33:23)\n   "
                " at Object.next"
                " (/snapshot/app/node_modules/flagsmith-nodejs/build/sdk/index.js:14:53)\n    at"
                " fulfilled (/snapshot/app/node_modules/flagsmith-nodejs/build/sdk/index.js:5:58)\n"
                "    at process.processTicksAndRejections (node:internal/process/task_queues:95:5)"
            ),
            errors=[
                {
                    "message": (
                        "[unexpectedRetrieving] Unexpected error when retrieving runtime"
                        " information. Please contact our support team if it occurs again. -- This"
                        " can be due to: Invalid request made to Flagsmith API. Response status"
                        " code: 502 | trace : Error: Invalid request made to Flagsmith API."
                        " Response status code: 502\n    at new FlagsmithAPIError"
                        " (/snapshot/app/node_modules/flagsmith-nodejs/build/sdk/errors.js:30:42)\n"
                        "    at Flagsmith.<anonymous>"
                        " (/snapshot/app/node_modules/flagsmith-nodejs/build/sdk/index.js:373:35)\n"
                        "    at step"
                        " (/snapshot/app/node_modules/flagsmith-nodejs/build/sdk/index.js:33:23)\n "
                        "   at Object.next"
                        " (/snapshot/app/node_modules/flagsmith-nodejs/build/sdk/index.js:14:53)\n "
                        "   at fulfilled"
                        " (/snapshot/app/node_modules/flagsmith-nodejs/build/sdk/index.js:5:58)\n  "
                        "  at process.processTicksAndRejections"
                        " (node:internal/process/task_queues:95:5)"
                    ),
                    "locations": [{"line": 2, "column": 3}],
                    "path": ["data"],
                    "extensions": {"code": "OPERATION_RESOLUTION_FAILURE"},
                }
            ],
            data={"data": None},
        )

    mocked_execute = mocker.patch.object(Client, "execute", side_effect=mocked_backend_response)

    # Given
    client = GraphQLClient(
        endpoint="",
        api_key="",
        client_name=GraphQLClientName.SDK,
        http_client=HttpClient(
            kili_endpoint="https://fake_endpoint.kili-technology.com", api_key="", verify=True
        ),
        enable_schema_caching=False,
    )

    # When
    result = client.execute(query="fake_query")

    # Then
    assert result["data"] == "all good"
    assert mocked_execute.call_count == nb_times_called == 3


@pytest.mark.parametrize(
    ("variables", "expected"),
    [
        ({"id": "123456"}, {"id": "123456"}),
        ({"id": None}, {}),
        (
            {
                "project": {"id": "project_id"},
                "asset": {"id": None},
                "assetIn": ["123456"],
                "status": "some_status",
                "type": None,
            },
            {
                "project": {"id": "project_id"},
                "asset": {},
                "assetIn": ["123456"],
                "status": "some_status",
            },
        ),
        (
            {
                "id": None,
                "searchQuery": "truc",
                "shouldRelaunchKpiComputation": None,
                "starred": True,
                "updatedAtGte": None,
                "updatedAtLte": None,
                "createdAtGte": None,
                "createdAtLte": None,
                "tagIds": ["tag_id"],
            },
            {
                "searchQuery": "truc",
                "starred": True,
                "tagIds": ["tag_id"],
            },
        ),
        (  # assetwhere
            {
                "externalIdStrictlyIn": ["truc"],
                "externalIdIn": None,
                "honeypotMarkGte": None,
                "honeypotMarkLte": 0.0,
                "id": "fake_asset_id",
                "metadata": {"key": None},  # this field is a JSON graphql type. It should be kept
                "project": {"id": "fake_proj_id"},
                "skipped": True,
                "updatedAtLte": None,
            },
            {
                "externalIdStrictlyIn": ["truc"],
                "honeypotMarkLte": 0.0,
                "id": "fake_asset_id",
                "metadata": {"key": None},
                "project": {"id": "fake_proj_id"},
                "skipped": True,
            },
        ),
    ],
)
def test_given_variables_when_i_remove_null_values_then_it_works(variables: dict, expected: dict):
    # Given
    _ = variables

    # When
    output = GraphQLClient._remove_nullable_inputs(variables)

    # Then
    assert output == expected
