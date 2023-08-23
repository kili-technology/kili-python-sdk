"""GraphQL gateway module."""
from kili.gateways.kili_api_gateway.issue import IssueOperationMixin


class KiliAPIGateway(IssueOperationMixin):
    """GraphQL gateway to communicate with Kili backend."""

    def __init__(self, graphql_client, http_client):
        self.graphql_client = graphql_client
        self.http_client = http_client
