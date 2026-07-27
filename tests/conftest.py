"""Common fixtures for tests."""

from collections.abc import Callable

import pytest
from gql import Client
from pytest_mock import MockerFixture

from kili.adapters.http_client import HttpClient
from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.core.graphql.clientnames import GraphQLClientName
from kili.core.graphql.graphql_client import GraphQLClient


@pytest.fixture()
def http_client(mocker: MockerFixture) -> HttpClient:
    return mocker.MagicMock(spec=HttpClient)


@pytest.fixture()
def graphql_client(mocker: MockerFixture) -> GraphQLClient:
    return mocker.MagicMock(spec=GraphQLClient)


@pytest.fixture()
def make_graphql_client() -> Callable[[str | None], GraphQLClient]:
    """Return a factory building a real GraphQLClient with the given SDL as its local schema.

    No network call is made. Pass None to get a client with no local schema at all. Used by the
    tests that must exercise the real schema introspection done by `GraphQLClient.supports_mutation`,
    which a mocked client would bypass.
    """

    def build(schema: str | None) -> GraphQLClient:
        client = GraphQLClient(
            endpoint="",
            api_key="",
            client_name=GraphQLClientName.SDK,
            http_client=HttpClient(
                kili_endpoint="https://fake_endpoint.kili-technology.com", api_key="", verify=True
            ),
            enable_schema_caching=False,
        )
        if schema is not None:
            client._gql_client = Client(schema=schema)
        return client

    return build


@pytest.fixture()
def kili_api_gateway(
    mocker: MockerFixture, graphql_client: GraphQLClient, http_client: HttpClient
) -> KiliAPIGateway:
    mock = mocker.MagicMock(spec=KiliAPIGateway)
    mock.graphql_client = graphql_client
    mock.http_client = http_client
    return mock
