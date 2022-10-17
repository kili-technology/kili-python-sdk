"""
Api key mutations
"""

from typeguard import typechecked

from ...helpers import format_result
from .queries import GQL_APPEND_TO_API_KEYS


class MutationsApiKey:  # pylint: disable=too-few-public-methods
    """Set of User mutations."""

    # pylint: disable=too-many-arguments,too-many-locals

    def __init__(self, auth):
        """Initialize the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    @typechecked
    def append_to_api_keys(self, api_key: str, name: str):
        """Create an api key to connect to the API.

        Args:
            api_key: A new api key to connect with
            name: A name used to describe the api key.

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.
        """
        variables = {
            "data": {"key": api_key, "name": name},
            "where": {"email": self.auth.user_email},
        }
        result = self.auth.client.execute(GQL_APPEND_TO_API_KEYS, variables)
        return format_result("data", result)
