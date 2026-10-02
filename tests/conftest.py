"""Common fixtures for tests."""

import pytest
from pytest_mock import MockerFixture

from kili.adapters.http_client import HttpClient
from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.core.graphql.graphql_client import GraphQLClient
from kili.core.utils.batching import mutation_batch_sizer, query_page_sizer


@pytest.fixture(autouse=True)
def _reset_batch_and_page_budgets():
    """The budgets are process-wide: a test must not inherit what another one measured."""
    mutation_batch_sizer.reset()
    query_page_sizer.reset()
    yield
    mutation_batch_sizer.reset()
    query_page_sizer.reset()


@pytest.fixture()
def http_client(mocker: MockerFixture) -> HttpClient:
    return mocker.MagicMock(spec=HttpClient)


@pytest.fixture()
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
