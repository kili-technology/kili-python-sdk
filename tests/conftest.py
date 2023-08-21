"""Common fixtures for tests."""

import pytest
import requests
from pytest_mock import MockerFixture

from kili.core.graphql.gateway import GraphQLGateway
from kili.core.graphql.graphql_client import GraphQLClient


@pytest.fixture()
def graphql_gateway(mocker: MockerFixture):
    mock = mocker.MagicMock(spec=GraphQLGateway)
    mock.graphql_client = mocker.MagicMock(spec=GraphQLClient)
    mock.http_client = mocker.MagicMock(spec=requests.Session)
    return mock
