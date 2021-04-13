from typing import List, Optional

from typeguard import typechecked

from ...helpers import Compatible, format_result, fragment_builder
from .queries import gql_notifications, GQL_NOTIFICATIONS_COUNT
from ...types import Notification


class QueriesNotification:

    def __init__(self, auth):
        """
        Initializes the subclass

        Parameters
        ----------
        - auth : KiliAuth object
        """
        self.auth = auth

    @Compatible(['v2'])
    @typechecked
    def notifications(self,
                      fields: List[str] = ['createdAt', 'hasBeenSeen',
                                           'id', 'message', 'status', 'userID'],
                      first: int = 100,
                      has_been_seen: Optional[bool] = None,
                      notification_id: Optional[str] = None,
                      skip: int = 0,
                      user_id: Optional[str] = None):
        """
        Get an array of notifications given a set of constraints

        Parameters
        ----------
        - fields : list of string, optional (default = ['createdAt', 'hasBeenSeen', 'id', 'message', 'status', 'userID'])
            All the fields to request among the possible fields for the notifications
            See [the documentation](https://cloud.kili-technology.com/docs/python-graphql-api/graphql-api/#notification) for all possible fields.
        - first : int (default = 100)
            Number of notifications to query
        - has_been_seen : bool, optional (default = None)
            If the notifications returned should have been seen.
        - notification_id : str, optional (default = None)
            If given, will return the notification which has this id
        - skip : int (default = 0)
            Number of notifications to skip (they are ordered by their date of creation, first to last).
        - user_id : string, optional (default = None)
            If given, returns the notifications of a specific user

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.
        """
        formatted_first = first if first else 100
        variables = {
            'where': {
                'id': notification_id,
                'user': {
                    'id': user_id,
                },
                'hasBeenSeen': has_been_seen,
            },
            'skip': skip,
            'first': formatted_first,
        }
        GQL_NOTIFICATIONS = gql_notifications(
            fragment_builder(fields, Notification))
        result = self.auth.client.execute(GQL_NOTIFICATIONS, variables)
        return format_result('data', result)

    @Compatible(['v2'])
    @typechecked
    def count_notifications(self,
                            has_been_seen: Optional[bool] = None,
                            user_id: Optional[str] = None):
        """
        Count the number of notifications

        Parameters
        ----------
        - has_been_seen : bool, optional (default = None)
            Filter on notifications that have been seen.
        - user_id : string, optional (default = None)
            Filter on the notifications of a specific user

        Returns
        -------
        - the number of notifications with the parameters provided
        """
        variables = {
            'where': {
                'user': {
                    'id': user_id,
                },
                'hasBeenSeen': has_been_seen,
            },
        }
        result = self.auth.client.execute(GQL_NOTIFICATIONS_COUNT, variables)
        count = format_result('data', result)
        return count
