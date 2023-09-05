"""Common fixtures for tests."""

import pytest
from pytest_mock import MockerFixture

from kili.adapters.http_client import HttpClient
from kili.adapters.kili_api_gateway import KiliAPIGateway
from kili.core.graphql.graphql_client import GraphQLClient


@pytest.fixture()
def kili_api_gateway(mocker: MockerFixture):
    mock = mocker.MagicMock(spec=KiliAPIGateway)
    mock.graphql_client = mocker.MagicMock(spec=GraphQLClient)
    mock.http_client = mocker.MagicMock(spec=HttpClient)
    return mock
