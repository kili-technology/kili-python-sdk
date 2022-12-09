"""
Api key mutations
"""

from typing import Dict

from typeguard import typechecked

from kili.graphql.operations.api_key import mutations


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
    def append_to_api_keys(self, api_key: str, name: str) -> Dict[str, str]:
        return mutations.append_to_api_keys(
            self.auth.client, email=self.auth.email, api_key=api_key, name=name
        )
