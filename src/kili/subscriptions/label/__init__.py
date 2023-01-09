"""Label subscription."""

from dataclasses import dataclass
from typing import Callable

from typeguard import typechecked

from ...graphql.graphql_client import SubscriptionGraphQLClient
from .subscriptions import GQL_LABEL_CREATED_OR_UPDATED


@dataclass
class SubscriptionsLabel:
    """Set of Label subscriptions."""

    # pylint: disable=too-many-arguments,too-many-locals

    def __init__(self, auth):
        """Initialize the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    @typechecked
    def label_created_or_updated(
        self, project_id: str, callback: Callable[[str, str], None]
    ) -> SubscriptionGraphQLClient:
        # pylint: disable=line-too-long
        """
        Subscribe a callback to a project, which is executed when a label is created or updated.

        Args:
            project_id: Identifier of the project
            callback: This function takes as input the id of the asset and its content.

        Returns:
            A subscription client.

        !!! example "Recipe"
            For more detailed examples on how to use Webhooks,
            See [the related recipe](https://github.com/kili-technology/kili-python-sdk/blob/master/recipes/webhooks.ipynb)
        """
        ws_endpoint = self.auth.client.endpoint.replace("http", "ws")
        websocket = SubscriptionGraphQLClient(ws_endpoint)
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        authorization = f"{self.auth.client.token}"
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
