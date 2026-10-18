import os
from time import time

import pytest
import pytest_mock
import requests
from gql import Client
from gql.transport import exceptions
from graphql import ExecutionResult
from pyrate_limiter import Duration, Rate
from pyrate_limiter.limiter import Limiter
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import ReadTimeout
from urllib3.exceptions import MaxRetryError, NewConnectionError

from kili.adapters.http_client import HttpClient
from kili.core.constants import MAX_CALLS_PER_MINUTE
from kili.core.graphql.graphql_client import GraphQLClient, GraphQLClientName
from kili.core.graphql.retry import MAX_ATTEMPTS_ON_UNCERTAIN_OUTCOME
from kili.exceptions import GraphQLError, MutationOutcomeUnknownError


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


def _client_with_backend(mocker: pytest_mock.MockerFixture, *responses):
    """A GraphQL client whose backend answers each call with the next response or error."""
    mocker.patch("kili.core.graphql.graphql_client._backoff", return_value=0)
    replies = iter(responses)

    def mocked_backend_response(*args, **kwargs):
        reply = next(replies)
        if isinstance(reply, BaseException):
            raise reply
        return ExecutionResult(reply, extensions=None)

    mocked_execute = mocker.patch.object(Client, "execute", side_effect=mocked_backend_response)
    client = GraphQLClient(
        endpoint="",
        api_key="",
        client_name=GraphQLClientName.SDK,
        http_client=HttpClient(
            kili_endpoint="https://fake_endpoint.kili-technology.com", api_key="", verify=True
        ),
        enable_schema_caching=False,
    )
    return client, mocked_execute


MUTATION = "mutation { appendManyAssets(data: {}) { id } }"
QUERY = "query { projects { id } }"
ENVOY_REFUSED = (
    "upstream connect error or disconnect/reset before headers. reset reason: remote connection"
    " failure, transport failure reason: delayed connect error: Connection refused"
)


def _refused_connection() -> RequestsConnectionError:
    reason = NewConnectionError(None, "Connection refused")  # type: ignore
    return RequestsConnectionError(MaxRetryError(None, "/graphql", reason))  # type: ignore


def _server_error(code: int, body: str = "", headers=None) -> exceptions.TransportServerError:
    response = requests.Response()
    response.status_code = code
    response._content = body.encode()  # pylint: disable=protected-access
    response.headers.update(headers or {})
    try:
        raise exceptions.TransportServerError(f"{code} Server Error", code) from requests.HTTPError(
            response=response
        )
    except exceptions.TransportServerError as error:
        return error


def test_given_a_mutation_when_the_answer_times_out_then_it_is_sent_once(
    mocker: pytest_mock.MockerFixture,
):
    client, mocked_execute = _client_with_backend(mocker, ReadTimeout(), {"data": "resent"})

    with pytest.raises(MutationOutcomeUnknownError, match="appendManyAssets") as raised:
        client.execute(MUTATION)

    assert mocked_execute.call_count == 1
    assert isinstance(raised.value, requests.ConnectionError)  # what callers caught before
    assert isinstance(raised.value.cause, ReadTimeout)


@pytest.mark.parametrize("status", [500, 502, 503, 504])
def test_given_a_mutation_when_a_proxy_answers_5xx_then_it_is_sent_once(
    mocker: pytest_mock.MockerFixture, status: int
):
    client, mocked_execute = _client_with_backend(mocker, _server_error(status), {"data": "x"})

    with pytest.raises(MutationOutcomeUnknownError):
        client.execute(MUTATION)

    assert mocked_execute.call_count == 1


@pytest.mark.parametrize(
    "error",
    [
        _refused_connection(),
        _server_error(429),
        _server_error(503, ENVOY_REFUSED),
        _server_error(401),
    ],
    ids=["refused", "429", "503 not forwarded", "401"],
)
def test_given_a_mutation_when_the_server_did_not_process_it_then_it_is_resent(
    mocker: pytest_mock.MockerFixture, error: Exception
):
    client, mocked_execute = _client_with_backend(mocker, error, {"data": "applied"})

    assert client.execute(MUTATION)["data"] == "applied"
    assert mocked_execute.call_count == 2


def test_given_the_server_rejects_requests_then_it_retries_until_the_deadline(
    mocker: pytest_mock.MockerFixture,
):
    client, mocked_execute = _client_with_backend(mocker, *[_refused_connection()] * 1000)
    mocker.patch("kili.core.graphql.graphql_client.RETRY_DEADLINE_SECONDS", 0.3)
    mocker.patch("kili.core.graphql.graphql_client._backoff", return_value=0.02)
    # the process-wide rate limiter would spend the deadline when other tests ran before
    mocker.patch("kili.core.graphql.graphql_client._limiter.try_acquire")

    with pytest.raises(RequestsConnectionError):
        client.execute(MUTATION)

    # far more than the attempts allowed on an uncertain outcome: only the deadline stops it
    assert mocked_execute.call_count > MAX_ATTEMPTS_ON_UNCERTAIN_OUTCOME


def test_given_a_query_when_the_answer_times_out_then_it_is_resent(
    mocker: pytest_mock.MockerFixture,
):
    client, mocked_execute = _client_with_backend(
        mocker, ReadTimeout(), _server_error(502), {"data": "ok"}
    )

    assert client.execute(QUERY)["data"] == "ok"
    assert mocked_execute.call_count == 3


def test_given_a_query_when_it_keeps_timing_out_then_it_is_resent_once(
    mocker: pytest_mock.MockerFixture,
):
    client, mocked_execute = _client_with_backend(mocker, *[ReadTimeout()] * 10)

    with pytest.raises(ReadTimeout):
        client.execute(QUERY)

    # a query that timed out was heavy: each attempt makes the backend redo it
    assert mocked_execute.call_count == 2


def test_given_a_query_when_the_connection_keeps_dropping_then_it_gives_up(
    mocker: pytest_mock.MockerFixture,
):
    client, mocked_execute = _client_with_backend(mocker, *[_server_error(502)] * 10)

    with pytest.raises(exceptions.TransportServerError):
        client.execute(QUERY)

    assert mocked_execute.call_count == MAX_ATTEMPTS_ON_UNCERTAIN_OUTCOME


def test_given_retry_disabled_when_the_connection_is_refused_then_it_is_not_resent(
    mocker: pytest_mock.MockerFixture,
):
    client, mocked_execute = _client_with_backend(mocker, _refused_connection())

    with pytest.raises(RequestsConnectionError):
        client.execute(MUTATION, retry=False)
    assert mocked_execute.call_count == 1


def test_given_a_429_with_retry_after_then_the_client_waits_what_the_server_asks(
    mocker: pytest_mock.MockerFixture,
):
    client, _ = _client_with_backend(
        mocker, _server_error(429, "", {"Retry-After": "0.2"}), {"data": "ok"}
    )
    sleep = mocker.patch("tenacity.nap.time.sleep")

    client.execute(MUTATION)

    sleep.assert_called_once_with(0.2)


def test_given_the_schema_introspection_fails_once_then_it_is_retried(
    mocker: pytest_mock.MockerFixture,
):
    client, _ = _client_with_backend(mocker)
    fetch = mocker.patch.object(
        client, "_fetch_graphql_schema_from_endpoint", side_effect=[_server_error(502), "schema"]
    )

    assert client._get_graphql_schema_from_endpoint() == "schema"
    assert fetch.call_count == 2


def test_given_short_retries_then_the_user_is_not_warned(mocker: pytest_mock.MockerFixture):
    client, _ = _client_with_backend(mocker, _refused_connection(), {"data": "ok"})
    warning = mocker.patch("kili.core.graphql.graphql_client.logger.warning")

    client.execute(MUTATION)

    warning.assert_not_called()


def test_given_retries_that_delay_the_user_then_they_are_told_once_and_told_the_outcome(
    mocker: pytest_mock.MockerFixture,
):
    client, _ = _client_with_backend(mocker, *[_refused_connection()] * 3, {"data": "ok"})
    mocker.patch("kili.core.graphql.graphql_client.WARN_AFTER_RETRYING_SECONDS", 0)
    warning = mocker.patch("kili.core.graphql.graphql_client.logger.warning")

    client.execute(MUTATION)

    messages = [call.args[0] % call.args[1:] for call in warning.call_args_list]
    assert len(messages) == 2
    assert messages[0].startswith("The Kili API could not process appendManyAssets (")
    assert "Retrying for up to" in messages[0]
    assert messages[1].startswith("appendManyAssets succeeded after")


@pytest.mark.parametrize(("status", "attempts"), [(500, 1), (504, 2), (524, 2)])
def test_given_a_query_the_server_failed_or_gave_up_on_then_it_is_resent_once_at_most(
    mocker: pytest_mock.MockerFixture, status: int, attempts: int
):
    client, mocked_execute = _client_with_backend(mocker, *[_server_error(status)] * 5)

    with pytest.raises(exceptions.TransportServerError):
        client.execute(QUERY)

    assert mocked_execute.call_count == attempts


def test_given_a_query_retried_a_bounded_number_of_times_then_the_warning_says_how_many(
    mocker: pytest_mock.MockerFixture,
):
    client, _ = _client_with_backend(mocker, _server_error(502), {"data": "ok"})
    mocker.patch("kili.core.graphql.graphql_client.WARN_AFTER_RETRYING_SECONDS", 0)
    warning = mocker.patch("kili.core.graphql.graphql_client.logger.warning")

    client.execute(QUERY)

    message = warning.call_args_list[0].args[0] % warning.call_args_list[0].args[1:]
    assert "Retrying, 4 attempt(s) left" in message
