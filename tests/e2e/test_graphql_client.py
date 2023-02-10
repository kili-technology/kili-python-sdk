"""
Test module for the GraphQL client
"""
from unittest import mock

import pytest
from gql.transport.exceptions import TransportQueryError
from graphql import GraphQLError

from kili.client import Kili


def test_gql_bad_query_local_validation():
    """test gql validation against local schema"""
    kili = Kili()  # fetch schema from kili server
    query = """
    query MyQuery {
        my_query_is_clearly_not_valid_according_to_the_kili_schema {
            id
        }
    }
    """

    mocked_transport_execute = mock.MagicMock()
    kili.auth.client.gql_transport.execute = mocked_transport_execute

    with pytest.raises(GraphQLError):
        kili.auth.client.execute(query)

    mocked_transport_execute.assert_not_called()


def test_gql_bad_query_remote_validation():
    """test gql validation against remote schema"""
    kili = Kili()

    query = """
    query MyQuery {
        my_query_is_clearly_not_valid_according_to_the_kili_schema {
            id
        }
    }
    """

    kili.auth.client.gql_client.schema = None
    kili.auth.client.gql_client.fetch_schema_from_transport = False
    mocked_validate = mock.MagicMock()
    kili.auth.client.gql_client.validate = mocked_validate

    with pytest.raises(TransportQueryError):
        kili.auth.client.execute(query)

    mocked_validate.assert_not_called()
