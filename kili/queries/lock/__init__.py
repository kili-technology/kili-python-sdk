import warnings

from ...helpers import deprecate, format_result, fragment_builder
from .queries import gql_locks
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

    def locks(self, 
              author_id : str = None,
              lock_id: str = None,
              lock_of_id : str = None,
              fields: list = ['id', 'lockType'],
              first: int = 100,
              skip: int = 0):
        """
        Get locks

        Returns locks

        Parameters
        ----------
        - lock_id : str, optional (default = None)
        - lock_of_id : str, optional (default = None)
            The id of the asset whose locks are requested
        - author_id : str, optional (default = None)
            The id of the user whose locks are requested
        - fields : list of string, optional (default = ['id', 'lock_type'])
            All the fields to request among the possible fields for the locks, default for None are the non-calculated fields)
            Possible fields : see https://cloud.kili-technology.com/docs/python-graphql-api/graphql-api/#locks
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
                'id': lock_id,
                'author' :{
                    'id': author_id
                }
                'lockOf' {
                    'id' : lock_of_id
                }
            }
        }
        GQL_LOCKS = gql_locks(fragment_builder(fields, Lock))
        result = self.auth.client.execute(GQL_LOCKS, variables)
        return format_result('data', result)
