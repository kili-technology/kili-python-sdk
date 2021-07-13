from typing import Optional
import warnings

from typeguard import typechecked

from ...helpers import Compatible, deprecate, format_result, fragment_builder
from .queries import gql_locks, GQL_LOCKS_COUNT
from ...types import Lock


class QueriesLock:

    def __init__(self, auth):
        """
        Initializes the subclass

        Parameters
        ----------
        - auth : KiliAuth object
        """
        self.auth = auth

    @Compatible(['v1', 'v2'])
    @typechecked
    def locks(self,
              lock_id: Optional[str] = None,
              fields: list = ['id', 'lockType'],
              first: int = 100,
              skip: int = 0):
        """
        Get locks

        Returns locks

        Parameters
        ----------
        - lock_id : str, optional (default = None)
            The id of the lock to request. If None, all locks are returned
        - fields : list of string, optional (default = ['id', 'lock_type'])
            All the fields to request among the possible fields for the locks.
            See [the documentation](https://cloud.kili-technology.com/docs/python-graphql-api/graphql-api/#locks) for all possible fields.
        - first : int, optional (default = 100)
            Maximum number of locks to return. Can only be between 0 and 100.
        - skip : int, optional (default = 0)
            Number of skipped locks (they are ordered by creation date)

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.
        """
        variables = {
            'first': first,
            'skip': skip,
            'where': {
                'id': lock_id
            }
        }
        GQL_LOCKS = gql_locks(fragment_builder(fields, Lock))
        result = self.auth.client.execute(GQL_LOCKS, variables)
        return format_result('data', result)

    @Compatible(['v1', 'v2'])
    @typechecked
    def count_locks(self:any):
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
