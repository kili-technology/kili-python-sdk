"""
Lock queries
"""

from typing import Generator, List, Optional, Union
import warnings
from typeguard import typechecked


from ...helpers import Compatible, deprecate, format_result, fragment_builder
from .queries import gql_locks, GQL_LOCKS_COUNT
from ...types import Lock
from ...utils import row_generator_from_paginated_calls


class QueriesLock:
    """
    Set of Lock queries
    """
    # pylint: disable=too-many-arguments,too-many-locals

    def __init__(self, auth):
        """
        Initializes the subclass

        Parameters
        ----------
        - auth : KiliAuth object
        """
        self.auth = auth

    # pylint: disable=dangerous-default-value
    @Compatible(['v1', 'v2'])
    @typechecked
    def locks(self,
              lock_id: Optional[str] = None,
              fields: list = ['id', 'lockType'],
              first: int = 100,
              skip: int = 0,
              disable_tqdm: bool = False,
              as_generator: bool = False) -> Union[List[dict], Generator[dict, None, None]]:
        # pylint: disable=line-too-long
        """
        Gets a generator or a list of locks respecting a set of criteria

        Parameters
        ----------
        - lock_id : str, optional (default = None)
            The id of the lock to request. If None, all locks are returned
        - fields : list of string, optional (default = ['id', 'lock_type'])
            All the fields to request among the possible fields for the locks.
            See [the documentation](https://cloud.kili-technology.com/docs/python-graphql-api/graphql-api/#locks) for all possible fields.
        - first : int, optional (default = 100)
            Maximum number of locks to return.
        - skip : int, optional (default = 0)
            Number of skipped locks (they are ordered by creation date)
        - disable_tqdm : bool, (default = False)
        - as_generator: bool, (default = False)
            If True, a generator on the API key is returned.

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.
        """
        if as_generator is False:
            warnings.warn("From 2022-05-18, the default return type will be a generator. Currently, the default return type is a list. \n"
                          "If you want to force the query return to be a list, you can already call this method with the argument as_generator=False",
                          DeprecationWarning)

        count_args = {}
        payload_query = {
            'where': {
                'id': lock_id
            }
        }

        disable_tqdm = disable_tqdm or as_generator or lock_id is not None

        locks_generator = row_generator_from_paginated_calls(
            skip,
            first,
            self.count_locks,
            count_args,
            self._query_locks,
            payload_query,
            fields,
            disable_tqdm
        )

        if as_generator:
            return locks_generator
        return list(locks_generator)

    def _query_locks(self,
                     skip: int,
                     first: int,
                     payload: dict,
                     fields: List[str]):

        payload.update({'skip': skip, 'first': first})
        _gql_locks = gql_locks(fragment_builder(fields, Lock))
        result = self.auth.client.execute(_gql_locks, payload)
        return format_result('data', result)

    @Compatible(['v1', 'v2'])
    @typechecked
    def count_locks(self: any):
        """
        Get the number of locks

        Parameters
        ----------

        Returns
        -------
        - the number of locks
        """
        variables = {
            'where': {
                'id': None
            }
        }
        result = self.auth.client.execute(GQL_LOCKS_COUNT, variables)
        count = format_result('data', result)
        return count
