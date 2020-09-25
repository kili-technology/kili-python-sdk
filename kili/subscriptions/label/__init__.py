from typing import Any, Callable

from ...helpers import format_result
from .subscriptions import GQL_LABEL_CREATED_OR_UPDATED
from ...graphql_client import SubscriptionGraphQLClient


class SubscriptionsLabel:
    def __init__(self, auth):
        """
        Initializes the subclass

        Parameters
        ----------
        - auth : KiliAuth object
        """
        self.auth = auth

    def label_created_or_updated(self, project_id: str, callback: Callable[[str, str], None]):
        """
        Subscribe a callback to a project, which is executed when a label is created or updated

        Parameters
        ----------
        - project_id : str
        - callback : function of (str, str) -> None
            This function takes as input the id of the asset and its content.

        Returns
        -------
        - None
        """
        ws_endpoint = self.auth.client.endpoint.replace('http', 'ws')
        ws = SubscriptionGraphQLClient(ws_endpoint)
        headers = {'Accept': 'application/json',
                'Content-Type': 'application/json'}
        authorization = f'{self.auth.client.token}'
        headers['Authorization'] = authorization
        variables = {'projectID': project_id}
        ws.subscribe(GQL_LABEL_CREATED_OR_UPDATED, variables=variables,
                    callback=callback, headers=headers, authorization=authorization)
