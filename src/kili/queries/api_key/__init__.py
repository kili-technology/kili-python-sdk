"""
Api key queries
"""

from typing import Dict, Iterable, List, Optional

from typeguard import typechecked

from kili.graphql import QueryOptions
from kili.graphql.operations.api_key.queries import APIKeyQuery, APIKeyWhere


class QueriesApiKey:
    """
    Set of ApiKey queries
    """

    # pylint: disable=too-many-arguments,too-many-locals

    def __init__(self, auth):
        """Initialize the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    # pylint: disable=dangerous-default-value
    @typechecked
    def api_keys(
        self,
        api_key_id: Optional[str] = None,
        user_id: Optional[str] = None,
        api_key: Optional[str] = None,
        skip: int = 0,
        fields: List[str] = ["id", "name", "createdAt", "revoked"],
        first: Optional[int] = None,
        disable_tqdm: bool = False,
        as_generator: bool = False,
    ) -> Iterable[Dict]:
        # pylint: disable=line-too-long
        """Get a generator or a list of API keys that match a set of constraints.

        !!! info
            You can only query your own API keys

        Args:
            api_key_id: Identifier of the API key to retrieve.
            user_id: Identifier of the user.
            api_key: Value of the API key.
            skip: Number of assets to skip (they are ordered by their date of creation, first to last).
            fields: All the fields to request among the possible fields for the assets.
                See [the documentation](https://docs.kili-technology.com/reference/graphql-api#apikey) for all possible fields.
            first: Maximum number of API keys to return.
            disable_tqdm: If `True`, the progress bar will be disabled.
            as_generator: If `True`, a generator on the API key is returned.

        Returns:
            A result object which contains the query if it was successful,
                or an error message.


        Examples:
            >>> kili.api_keys(user_id=user_id)
            >>> kili.api_keys(api_key=api_key)
            >>> kili.api_keys(api_key=api_key, as_generator=False)
        """
        where = APIKeyWhere(api_key_id=api_key_id, user_id=user_id, api_key=api_key)
        options = QueryOptions(disable_tqdm, first, skip, as_generator)
        return APIKeyQuery(self.auth.client)(where, fields, options)

    @typechecked
    def count_api_keys(
        self,
        api_key_id: Optional[str] = None,
        user_id: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> int:
        """Count and return the number of api keys with the given constraints.

        Args:
            api_key_id: Identifier of the API key to retrieve.
            user_id: Identifier of the user.
            api_key: Value of the api key.

        Returns:
            A result object which contains the query if it was successful,
                or an error message.

        Examples:
            >>> kili.count_api_keys(user_id=user_id)
            3
            >>> kili.count_api_keys(api_key=api_key)
            1
        """
        where = APIKeyWhere(api_key_id=api_key_id, user_id=user_id, api_key=api_key)
        return APIKeyQuery(self.auth.client).count(where)
