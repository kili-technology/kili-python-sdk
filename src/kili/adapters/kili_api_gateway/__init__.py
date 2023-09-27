"""Kili API Gateway module for interacting with Kili."""

from typing import Optional

from kili.adapters.http_client import HttpClient
from kili.adapters.kili_api_gateway.api_key import ApiKeyOperationMixin
from kili.adapters.kili_api_gateway.asset import AssetOperationMixin
from kili.adapters.kili_api_gateway.issue import IssueOperationMixin
from kili.adapters.kili_api_gateway.project import ProjectOperationMixin
from kili.adapters.kili_api_gateway.tag import TagOperationMixin
from kili.core.graphql.graphql_client import GraphQLClient


class KiliAPIGateway(
    IssueOperationMixin,
    AssetOperationMixin,
    ProjectOperationMixin,
    TagOperationMixin,
    ApiKeyOperationMixin,
):
    """GraphQL gateway to communicate with Kili backend."""

    def __init__(self, graphql_client: GraphQLClient, http_client: HttpClient) -> None:
        """Initialize the Kili API Gateway."""
        self.graphql_client = graphql_client
        self.http_client = http_client

    def get_kili_app_version(self) -> Optional[str]:
        """Get the version of the Kili app server.

        Returns None if the version cannot be retrieved.
        """
        url = self.graphql_client.endpoint.replace("/graphql", "/version")
        response = self.http_client.get(url, timeout=30)
        if response.status_code == 200 and '"version":' in response.text:  # noqa: PLR2004
            response_json = response.json()
            return response_json["version"]
        return None
