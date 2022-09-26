"""
Lock queries
"""

from typing import Generator, List, Optional, Union

from typeguard import typechecked

from ...helpers import Compatible, format_result, fragment_builder
from ...types import Lock
from ...utils.pagination import row_generator_from_paginated_calls
from .queries import GQL_LOCKS_COUNT, gql_locks


class QueriesLock:
    """
    Set of Lock queries
    """

    # pylint: disable=too-many-arguments,too-many-locals

    def __init__(self, auth):
        """Initialize the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    # pylint: disable=dangerous-default-value
    @Compatible(["v1", "v2"])
    @typechecked
    def locks(
        self,
        lock_id: Optional[str] = None,
        fields: List[str] = ["id", "lockType"],
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: bool = False,
        as_generator: bool = False,
    ) -> Union[List[dict], Generator[dict, None, None]]:
        # pylint: disable=line-too-long
        """Get a generator or a list of locks respecting a set of criteria.

        Args:
            lock_id: The id of the lock to request. If None, all locks are returned
            fields: All the fields to request among the possible fields for the locks.
                See [the documentation](https://cloud.kili-technology.com/docs/python-graphql-api/graphql-api/#locks)
                for all possible fields.
            first: Maximum number of locks to return.
            skip: Number of skipped locks (they are ordered by creation date)
            disable_tqdm: If `True`, the progress bar will be disabled
            as_generator: If `True`, a generator on the API key is returned.

        Returns:
            A result object which contains the query if it was successful,
                or an error message.
        """

        count_args = {}
        payload_query = {"where": {"id": lock_id}}

        disable_tqdm = disable_tqdm or as_generator or lock_id is not None

        locks_generator = row_generator_from_paginated_calls(
            skip,
            first,
            self.count_locks,
            count_args,
            self._query_locks,
            payload_query,
            fields,
            disable_tqdm,
        )

        if as_generator:
            return locks_generator
        return list(locks_generator)

    def _query_locks(self, skip: int, first: int, payload: dict, fields: List[str]):

        payload.update({"skip": skip, "first": first})
        _gql_locks = gql_locks(fragment_builder(fields, Lock))
        result = self.auth.client.execute(_gql_locks, payload)
        return format_result("data", result)

    @Compatible(["v1", "v2"])
    @typechecked
    def count_locks(self: any) -> int:
        """Get the number of locks

        Args:

        Returns:
            The number of locks
        """
        variables = {"where": {"id": None}}
        result = self.auth.client.execute(GQL_LOCKS_COUNT, variables)
        count = format_result("data", result)
        return count
