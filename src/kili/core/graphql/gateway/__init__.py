"""GraphQL gateway module."""
from kili.core.graphql.gateway.issue import IssueOperationMixin


class GraphQLGateway(IssueOperationMixin):
    """GraphQL gateway to communicate with Kili backend."""

    def __init__(self, graphql_client, http_client):
        self.graphql_client = graphql_client
        self.http_client = http_client
