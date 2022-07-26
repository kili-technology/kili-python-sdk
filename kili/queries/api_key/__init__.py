"""
Api key queries
"""

from typing import Generator, List, Optional, Union

from typeguard import typechecked

from ...helpers import Compatible, format_result, fragment_builder
from ...types import ApiKey as ApiKeyType
from ...utils.pagination import row_generator_from_paginated_calls
from .queries import GQL_API_KEYS_COUNT, gql_api_keys


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
    @Compatible(["v2"])
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
    ) -> Union[List[dict], Generator[dict, None, None]]:
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
                See [the documentation](https://cloud.kili-technology.com/docs/python-graphql-api/graphql-api/#apikey) for all possible fields.
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

        saved_args = locals()
        count_args = {
            k: v for (k, v) in saved_args.items() if k in ["user_id", "api_key_id", "api_key"]
        }
        disable_tqdm = disable_tqdm or as_generator

        payload_query = {
            "where": {
                "user": {"id": user_id, "apiKey": api_key},
                "id": api_key_id,
            },
        }

        api_keys_generator = row_generator_from_paginated_calls(
            skip,
            first,
            self.count_api_keys,
            count_args,
            self._query_api_keys,
            payload_query,
            fields,
            disable_tqdm,
        )

        if as_generator:
            return api_keys_generator
        return list(api_keys_generator)

    def _query_api_keys(self, skip: int, first: int, payload: dict, fields: List[str]):

        payload.update({"skip": skip, "first": first})
        _gql_api_keys = gql_api_keys(fragment_builder(fields, ApiKeyType))
        result = self.auth.client.execute(_gql_api_keys, payload)
        return format_result("data", result)

    @Compatible(["v2"])
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
        variables = {
            "where": {
                "user": {"id": user_id, "apiKey": api_key},
                "id": api_key_id,
            },
        }
        result = self.auth.client.execute(GQL_API_KEYS_COUNT, variables)
        count = format_result("data", result)
        return count
