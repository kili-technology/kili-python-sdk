"""Kili API Gateway module for interacting with Kili."""

from kili.adapters.http_client import HttpClient
from kili.adapters.kili_api_gateway.api_key.operations_mixin import ApiKeyOperationMixin
from kili.adapters.kili_api_gateway.asset.operations_mixin import AssetOperationMixin
from kili.adapters.kili_api_gateway.cloud_storage import CloudStorageOperationMixin
from kili.adapters.kili_api_gateway.issue import IssueOperationMixin
from kili.adapters.kili_api_gateway.label.operations_mixin import LabelOperationMixin
from kili.adapters.kili_api_gateway.llm.operations_mixin import (
    ModelConfigurationOperationMixin,
)
from kili.adapters.kili_api_gateway.notification.operations_mixin import (
    NotificationOperationMixin,
)
from kili.adapters.kili_api_gateway.organization.operations_mixin import (
    OrganizationOperationMixin,
)
from kili.adapters.kili_api_gateway.project.operations_mixin import ProjectOperationMixin
from kili.adapters.kili_api_gateway.tag import TagOperationMixin
from kili.adapters.kili_api_gateway.user.operation_mixin import UserOperationMixin
from kili.core.graphql.graphql_client import GraphQLClient


class KiliAPIGateway(
    ApiKeyOperationMixin,
    AssetOperationMixin,
    CloudStorageOperationMixin,
    IssueOperationMixin,
    LabelOperationMixin,
    ModelConfigurationOperationMixin,
    NotificationOperationMixin,
    OrganizationOperationMixin,
    ProjectOperationMixin,
    TagOperationMixin,
    UserOperationMixin,
):
    """GraphQL gateway to communicate with Kili backend."""

    def __init__(self, graphql_client: GraphQLClient, http_client: HttpClient) -> None:
        """Initialize the Kili API Gateway."""
        self.graphql_client = graphql_client
        self.http_client = http_client
