from typing import Any, Callable

from ...helpers import format_result
from .subscriptions import GQL_LABEL_CREATED_OR_UPDATED
from ...graphql_client import SubscriptionGraphQLClient


def label_created_or_updated(client, project_id: str, callback: Callable[[str, str], None]):
    ws_endpoint = client.endpoint.replace('http', 'ws')
    ws = SubscriptionGraphQLClient(ws_endpoint)
    headers = {'Accept': 'application/json',
               'Content-Type': 'application/json'}
    headers['Authorization'] = f'{client.token}'
    variables = {'projectID': project_id}
    ws.subscribe(GQL_LABEL_CREATED_OR_UPDATED, variables=variables,
                 callback=callback, headers=headers)
