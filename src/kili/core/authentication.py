"""API authentication module."""
import warnings
from datetime import datetime, timedelta
from typing import Dict

import requests

from kili import __version__
from kili.core.graphql import QueryOptions
from kili.core.graphql.graphql_client import GraphQLClient, GraphQLClientName
from kili.core.graphql.operations.api_key.queries import APIKeyQuery, APIKeyWhere
from kili.core.graphql.operations.user.queries import GQL_ME
from kili.core.helpers import format_result

from ..exceptions import AuthenticationFailed, UserNotFoundError

warnings.filterwarnings("default", module="kili", category=DeprecationWarning)


class KiliAuth:
    """Kili authentication class."""

    def __init__(
        self, api_key: str, api_endpoint: str, client_name: GraphQLClientName, verify=True
    ) -> None:
        self.api_key = api_key
        self.api_endpoint = api_endpoint
        self.client_name = client_name
        self.verify = verify

        self.check_api_key_valid()

        self.client = GraphQLClient(
            endpoint=api_endpoint,
            api_key=api_key,
            client_name=client_name,
            verify=self.verify,
        )

        self.check_expiry_of_key_is_close()

        user = self.get_user()
        self.user_id = user["id"]
        self.user_email = user["email"]

    def check_api_key_valid(self) -> None:
        """Check that the api_key provided is valid."""
        response = requests.post(
            url=self.api_endpoint,
            data='{"query":"{ me { id email } }"}',
            verify=self.verify,
            timeout=30,
            headers={
                "Authorization": f"X-API-Key: {self.api_key}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "apollographql-client-name": self.client_name.value,
                "apollographql-client-version": __version__,
            },
        )
        if response.status_code == 200 and "email" in response.text and "id" in response.text:
            return

        raise AuthenticationFailed(
            api_key=self.api_key,
            api_endpoint=self.api_endpoint,
            error_msg=(
                "Cannot check API key validity: status_code"
                f" {response.status_code}\n\n{response.text}"
            ),
        )

    def check_expiry_of_key_is_close(self) -> None:
        """Check that the expiration date of the api_key is not too close."""
        warn_days = 30

        api_keys = APIKeyQuery(self.client)(
            fields=["expiryDate"],
            where=APIKeyWhere(api_key=self.api_key),
            options=QueryOptions(disable_tqdm=True),
        )

        key_expiry = datetime.strptime(next(api_keys)["expiryDate"], r"%Y-%m-%dT%H:%M:%S.%fZ")
        key_remaining_time = key_expiry - datetime.now()
        key_soon_deprecated = key_remaining_time < timedelta(days=warn_days)
        if key_soon_deprecated:
            message = f"""
                Your api key will be deprecated on {key_expiry:%Y-%m-%d}.
                You should generate a new one on My account > API KEY."""
            warnings.warn(message, UserWarning, stacklevel=2)

    def get_user(self) -> Dict:
        """Get the current user from the api_key provided."""
        result = self.client.execute(GQL_ME)
        user = format_result("data", result)
        if user is None or user["id"] is None or user["email"] is None:
            raise UserNotFoundError("No user attached to the API key was found")
        return user
