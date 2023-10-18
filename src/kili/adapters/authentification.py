"""Authentification functions that does not rely on the graphQL client."""

from kili import __version__
from kili.adapters.http_client import HttpClient
from kili.core.graphql.clientnames import GraphQLClientName
from kili.utils.logcontext import LogContext, log_call


@log_call
def is_api_key_valid(
    http_client: HttpClient,
    api_key: str,
    api_endpoint: str,
    client_name: GraphQLClientName,
) -> bool:
    """Check that the api_key provided is valid.

    Note that this method does not rely on the GraphQL client, but on the HTTP client.
    It must stay this way since the GraphQL client might retry in case of 401 http error.
    """
    response = http_client.post(
        url=api_endpoint,
        data='{"query":"{ me { id email } }"}',
        timeout=30,
        headers={
            "Authorization": f"X-API-Key: {api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "apollographql-client-name": client_name.value,
            "apollographql-client-version": __version__,
            **LogContext(),
        },
    )
    return (
        response.status_code == 200  # noqa: PLR2004
        and "email" in response.text
        and "id" in response.text
    )
