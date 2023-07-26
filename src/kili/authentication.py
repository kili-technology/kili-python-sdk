"""API authentication module"""
import warnings
from datetime import datetime, timedelta
from typing import Dict, Union

import requests

from kili import __version__
from kili.graphql import QueryOptions
from kili.graphql.graphql_client import GraphQLClient, GraphQLClientName
from kili.graphql.operations.api_key.queries import APIKeyQuery, APIKeyWhere
from kili.graphql.operations.user.queries import GQL_ME
from kili.helpers import format_result

from .exceptions import AuthenticationFailed, UserNotFoundError

warnings.filterwarnings("default", module="kili", category=DeprecationWarning)


def get_version_without_patch(version):
    """Return the version of Kili API removing the patch version.

    Args:
        version
    """
    return ".".join(version.split(".")[:-1])


# pylint: disable=too-many-instance-attributes
class KiliAuth:
    """
    Kili authentication class
    """

    def __init__(
        self,
        api_key: str,
        api_endpoint: str,
        client_name: GraphQLClientName,
        ssl_verify: Union[bool, str],
    ) -> None:
        self.api_key = api_key
        self.api_endpoint = api_endpoint
        self.client_name = client_name
        self.ssl_verify = ssl_verify

        try:
            self.endpoint_kili_version = self.check_versions_match()
        except:  # pylint: disable=bare-except
            message = (
                "We could not check the version, there might be a version"
                "mismatch or the app might be in deployment"
            )
            warnings.warn(message, UserWarning, stacklevel=2)

        self.check_api_key_valid()

        self.client = GraphQLClient(
            endpoint=api_endpoint,
            api_key=api_key,
            client_name=client_name,
            ssl_verify=self.ssl_verify,
        )

        self.check_expiry_of_key_is_close()

        user = self.get_user()
        self.user_id = user["id"]
        self.user_email = user["email"]

    def check_versions_match(self) -> str:
        """Check that the versions of Kili Python SDK and Kili API are the same

        Args:
            api_endpoint: url of the Kili API
        """
        url = self.api_endpoint.replace("/graphql", "/version")
        response = requests.get(url, verify=self.ssl_verify, timeout=30).json()
        version = response["version"]
        if get_version_without_patch(version) != get_version_without_patch(__version__):
            message = (
                "Kili Python SDK version should match with Kili API version.\n"
                + f'Please install version: "pip install kili=={version}"'
            )
            warnings.warn(message, UserWarning, stacklevel=2)
        return version

    def check_api_key_valid(self) -> None:
        """Check that the api_key provided is valid"""
        response = requests.post(
            url=self.api_endpoint,
            data='{"query":"{ me { id email } }"}',
            verify=self.ssl_verify,
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
        """Check that the expiration date of the api_key is not too close.

        Args:
            api_key: key used to connect to the Kili API
        """
        warn_days = 30

        api_keys = APIKeyQuery(self.client, self.ssl_verify)(
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
        """Get the current user from the api_key provided"""
        result = self.client.execute(GQL_ME)
        user = format_result("data", result, None, self.ssl_verify)
        if user is None or user["id"] is None or user["email"] is None:
            raise UserNotFoundError("No user attached to the API key was found")
        return user
