"""Label subscription."""

from typing import Callable

from typeguard import typechecked

from kili.core.graphql.graphql_client import GraphQLClient
from kili.core.graphql.ws_graphql_client import SubscriptionGraphQLClient

from .subscriptions import GQL_LABEL_CREATED_OR_UPDATED


# pylint: disable=too-few-public-methods
class SubscriptionsLabel:
    """Set of Label subscriptions."""

    graphql_client: GraphQLClient

    @typechecked
    def label_created_or_updated(
        self, project_id: str, callback: Callable[[str, str], None]
    ) -> SubscriptionGraphQLClient:
        # pylint: disable=line-too-long
        """Subscribe a callback to a project, which is executed when a label is created or updated.

        Args:
            project_id: Identifier of the project
            callback: This function takes as input the id of the asset and its content.

        Returns:
            A subscription client.

        !!! example "Recipe"
            For more detailed examples on how to use Webhooks,
            See [the related recipe](https://github.com/kili-technology/kili-python-sdk/blob/main/recipes/webhooks_example.ipynb)
        """
        ws_endpoint = self.graphql_client.endpoint.replace("http", "ws")
        websocket = SubscriptionGraphQLClient(ws_endpoint)
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        authorization = f"X-API-Key: {self.api_key}"  # type: ignore  # pylint: disable=no-member
        headers["Authorization"] = authorization
        variables = {"projectID": project_id}
        websocket.subscribe(
            GQL_LABEL_CREATED_OR_UPDATED,
            variables=variables,
            callback=callback,
            headers=headers,
            authorization=authorization,
        )
        return websocket
