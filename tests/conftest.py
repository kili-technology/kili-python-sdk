"""Common fixtures for tests."""

import pytest
from pytest_mock import MockerFixture

from kili.adapters.http_client import HttpClient
from kili.adapters.kili_api_gateway import KiliAPIGateway
from kili.core.graphql.graphql_client import GraphQLClient


@pytest.fixture
def http_client(mocker: MockerFixture) -> HttpClient:
    return mocker.MagicMock(spec=HttpClient)


@pytest.fixture
def graphql_client(mocker: MockerFixture) -> GraphQLClient:
    return mocker.MagicMock(spec=GraphQLClient)


@pytest.fixture()
def kili_api_gateway(
    mocker: MockerFixture, graphql_client: GraphQLClient, http_client: HttpClient
) -> KiliAPIGateway:
    mock = mocker.MagicMock(spec=KiliAPIGateway)
    mock.graphql_client = graphql_client
    mock.http_client = http_client
    return mock
