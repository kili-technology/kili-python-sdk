"""
Notification queries
"""

from typing import Generator, List, Optional, Union
import warnings

from typeguard import typechecked


from ...helpers import Compatible, format_result, fragment_builder
from .queries import gql_notifications, GQL_NOTIFICATIONS_COUNT
from ...types import Notification
from ...utils import row_generator_from_paginated_calls


class QueriesNotification:
    """
    Set of Notification queries
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
    @Compatible(['v2'])
    @typechecked
    def notifications(self,
                      fields: List[str] = ['createdAt', 'hasBeenSeen',
                                           'id', 'message', 'status', 'userID'],
                      first: int = 100,
                      has_been_seen: Optional[bool] = None,
                      notification_id: Optional[str] = None,
                      skip: int = 0,
                      user_id: Optional[str] = None,
                      disable_tqdm: bool = False,
                      as_generator: bool = False) -> Union[List[dict], Generator[dict, None, None]]:
        # pylint: disable=line-too-long
        """
        Gets a generator or a list of notifications respecting a set of criteria

        Parameters
        ----------
        - fields : list of string, optional (default = ['createdAt', 'hasBeenSeen',
                'id', 'message', 'status', 'userID'])
            All the fields to request among the possible fields for the notifications
            See [the documentation](https://cloud.kili-technology.com/docs/python-graphql-api/graphql-api/#notification) for all possible fields.
        - first : int (default = 100)
            Number of notifications to query
        - has_been_seen : bool, optional (default = None)
            If the notifications returned should have been seen.
        - notification_id : str, optional (default = None)
            If given, will return the notification which has this id
        - skip : int (default = 0)
            Number of notifications to skip (they are ordered by their date of creation,
            first to last).
        - user_id : string, optional (default = None)
            If given, returns the notifications of a specific user
        - disable_tqdm : bool, (default = False)
        - as_generator: bool, (default = False)
            If True, a generator on the notifications is returned.

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.
        """
        if as_generator is False:
            warnings.warn("From 2022-05-18, the default return type will be a generator. Currently, the default return type is a list. \n"
                          "If you want to force the query return to be a list, you can already call this method with the argument as_generator=False",
                          DeprecationWarning)

        count_args = {"has_been_seen": has_been_seen, "user_id": user_id}
        disable_tqdm = disable_tqdm or as_generator or notification_id is not None
        payload_query = {
            'where': {
                'id': notification_id,
                'user': {
                    'id': user_id,
                },
                'hasBeenSeen': has_been_seen,
            },
        }
        notifications_generator = row_generator_from_paginated_calls(
            skip,
            first,
            self.count_notifications,
            count_args,
            self._query_notifications,
            payload_query,
            fields,
            disable_tqdm
        )

        if as_generator:
            return notifications_generator
        return list(notifications_generator)

    def _query_notifications(self,
                             skip: int,
                             first: int,
                             payload: dict,
                             fields: List[str]):

        payload.update({'skip': skip, 'first': first})
        _gql_notifications = gql_notifications(
            fragment_builder(fields, Notification))
        result = self.auth.client.execute(_gql_notifications, payload)
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
