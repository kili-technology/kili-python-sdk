"""Common fixtures for tests."""

import pytest
from pytest_mock import MockerFixture

from kili.adapters.http_client import HttpClient
from kili.adapters.kili_api_gateway import KiliAPIGateway
from kili.core.graphql.graphql_client import GraphQLClient


@pytest.fixture()
def mocked_graphql_client(mocker: MockerFixture):
    return mocker.MagicMock(spec=GraphQLClient)


@pytest.fixture()
def mocked_http_client(mocker: MockerFixture):
    return mocker.MagicMock(spec=HttpClient)


@pytest.fixture()
def mocked_kili_api_gateway(
    mocker: MockerFixture, mocked_graphql_client: GraphQLClient, mocked_http_client: HttpClient
) -> KiliAPIGateway:
    mock = mocker.MagicMock(spec=KiliAPIGateway)
    mock.graphql_client = mocked_graphql_client
    mock.http_client = mocked_http_client
    return mock
