"""
Lock queries
"""

from typing import Dict, Iterable, List, Optional

from typeguard import typechecked

from kili.graphql import QueryOptions
from kili.graphql.operations.lock.queries import LockQuery, LockWhere
from kili.helpers import deprecate


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
    @typechecked
    @deprecate(
        "locks method is for internal use only and will be removed from 01/02/2013",
        removed_in="2.129",
    )
    def locks(
        self,
        lock_id: Optional[str] = None,
        fields: List[str] = ["id", "lockType"],
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: bool = False,
        as_generator: bool = False,
    ) -> Iterable[Dict]:
        # pylint: disable=line-too-long
        """Get a generator or a list of locks respecting a set of criteria.

        Args:
            lock_id: The id of the lock to request. If None, all locks are returned
            fields: All the fields to request among the possible fields for the locks.
                See [the documentation](https://docs.kili-technology.com/reference/graphql-api#locks)
                for all possible fields.
            first: Maximum number of locks to return.
            skip: Number of skipped locks (they are ordered by creation date)
            disable_tqdm: If `True`, the progress bar will be disabled
            as_generator: If `True`, a generator on the API key is returned.

        Returns:
            A result object which contains the query if it was successful,
                or an error message.
        """

        where = LockWhere(lock_id=lock_id)
        options = QueryOptions(disable_tqdm, first, skip, as_generator)
        return LockQuery(self.auth.client)(where, fields, options)

    @typechecked
    @deprecate(
        "count_locks method is for internal use only and will be removed from 01/02/2013",
        removed_in="2.129",
    )
    def count_locks(self, lock_id: Optional[str] = None) -> int:
        """Get the number of locks

        Args:

        Returns:
            The number of locks
        """
        where = LockWhere(lock_id=lock_id)
        return LockQuery(self.auth.client).count(where)
