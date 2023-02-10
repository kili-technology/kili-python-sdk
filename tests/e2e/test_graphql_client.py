"""
Test module for the GraphQL client
"""
from unittest import mock

import pytest
from graphql import GraphQLError

from kili.client import Kili


def test_gql_bad_query_local_validation():
    """test gql validation against local schema"""
    kili = Kili()
    query = '{"query":"{ my_query_is_clearly_not_valid_according_to_the_kili_schema { id } }"}'

    mocked_transport_execute = mock.MagicMock()
    kili.auth.client.gql_transport.execute = mocked_transport_execute

    with pytest.raises(GraphQLError):
        kili.auth.client.execute(query)

    mocked_transport_execute.assert_not_called()
