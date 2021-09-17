"""
Label subscription
"""

from dataclasses import dataclass
from typing import Any, Callable

from typeguard import typechecked

from .subscriptions import GQL_LABEL_CREATED_OR_UPDATED
from ...graphql_client import SubscriptionGraphQLClient


@dataclass
class SubscriptionsLabel:
    """
    Set of Label subscriptions
    """
    # pylint: disable=too-many-arguments,too-many-locals

    def __init__(self, auth):
        """
        Initializes the subclass

        Parameters
        ----------
        - auth : KiliAuth object
        """
        self.auth = auth

    @typechecked
    def label_created_or_updated(self, project_id: str, callback: Callable[[str, str], None]):
        # pylint: disable=line-too-long
        """
        Subscribe a callback to a project, which is executed when a label is created or updated.
        See [the related recipe](https://github.com/kili-technology/kili-playground/blob/master/recipes/webhooks.ipynb) for more explanation on how to use it.

        Parameters
        ----------
        - project_id : str
        - callback : function of (str, str) -> None
            This function takes as input the id of the asset and its content.

        Returns
        -------
        - subscription client
        """
        ws_endpoint = self.auth.client.endpoint.replace('http', 'ws')
        websocket = SubscriptionGraphQLClient(ws_endpoint)
        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json'}
        authorization = f'{self.auth.client.token}'
        headers['Authorization'] = authorization
        variables = {'projectID': project_id}
        websocket.subscribe(
            GQL_LABEL_CREATED_OR_UPDATED,
            variables=variables,
            callback=callback,
            headers=headers,
            authorization=authorization)
        return websocket
