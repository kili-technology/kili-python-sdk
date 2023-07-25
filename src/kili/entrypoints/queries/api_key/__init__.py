"""Api key queries."""

from typing import Dict, Generator, Iterable, List, Literal, Optional, overload

from typeguard import typechecked

from kili.core.graphql import QueryOptions
from kili.core.graphql.operations.api_key.queries import APIKeyQuery, APIKeyWhere
from kili.core.helpers import disable_tqdm_if_as_generator
from kili.entrypoints.base import BaseOperationEntrypointMixin
from kili.utils.logcontext import for_all_methods, log_call


@for_all_methods(log_call, exclude=["__init__"])
class QueriesApiKey(BaseOperationEntrypointMixin):
    """Set of ApiKey queries."""

    # pylint: disable=too-many-arguments,dangerous-default-value
    @overload
    def api_keys(
        self,
        api_key_id: Optional[str] = None,
        user_id: Optional[str] = None,
        api_key: Optional[str] = None,
        skip: int = 0,
        fields: List[str] = ["id", "name", "createdAt", "revoked"],
        first: Optional[int] = None,
        disable_tqdm: bool = False,
        *,
        as_generator: Literal[True],
    ) -> Generator[Dict, None, None]:
        ...

    @overload
    def api_keys(
        self,
        api_key_id: Optional[str] = None,
        user_id: Optional[str] = None,
        api_key: Optional[str] = None,
        skip: int = 0,
        fields: List[str] = ["id", "name", "createdAt", "revoked"],
        first: Optional[int] = None,
        disable_tqdm: bool = False,
        *,
        as_generator: Literal[False] = False,
    ) -> List[Dict]:
        ...

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
        *,
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
        disable_tqdm = disable_tqdm_if_as_generator(as_generator, disable_tqdm)
        options = QueryOptions(disable_tqdm, first, skip)
        api_keys_gen = APIKeyQuery(self.graphql_client, self.http_client)(where, fields, options)

        if as_generator:
            return api_keys_gen
        return list(api_keys_gen)

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
            The number of API Keys matching params if it was successful,
                or an error message.

        Examples:
            >>> kili.count_api_keys(user_id=user_id)
            3
            >>> kili.count_api_keys(api_key=api_key)
            1
        """
        where = APIKeyWhere(api_key_id=api_key_id, user_id=user_id, api_key=api_key)
        return APIKeyQuery(self.graphql_client, self.http_client).count(where)
