"""Common fixtures for tests."""

import pytest
import requests
from pytest_mock import MockerFixture

from kili.core.graphql.graphql_client import GraphQLClient
from kili.gateways.kili_api_gateway import KiliAPIGateway


@pytest.fixture()
def kili_api_gateway(mocker: MockerFixture):
    mock = mocker.MagicMock(spec=KiliAPIGateway)
    mock.graphql_client = mocker.MagicMock(spec=GraphQLClient)
    mock.http_client = mocker.MagicMock(spec=requests.Session)
    return mock
