"""Notification queries."""

from typing import Dict, Iterable, List, Optional

from typeguard import typechecked

from kili.graphql import QueryOptions
from kili.graphql.operations.notification.queries import (
    NotificationQuery,
    NotificationWhere,
)


class QueriesNotification:
    """Set of Notification queries."""

    # pylint: disable=too-many-arguments,too-many-locals

    def __init__(self, auth):
        """Initialize the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    # pylint: disable=dangerous-default-value
    @typechecked
    def notifications(
        self,
        fields: List[str] = [
            "createdAt",
            "hasBeenSeen",
            "id",
            "message",
            "status",
            "userID",
        ],
        first: Optional[int] = None,
        has_been_seen: Optional[bool] = None,
        notification_id: Optional[str] = None,
        skip: int = 0,
        user_id: Optional[str] = None,
        disable_tqdm: bool = False,
        as_generator: bool = False,
    ) -> Iterable[Dict]:
        # pylint: disable=line-too-long
        """Get a generator or a list of notifications respecting a set of criteria.

        Args:
            fields: All the fields to request among the possible fields for the notifications
                See [the documentation](https://docs.kili-technology.com/reference/graphql-api#notification) for all possible fields.
            first: Number of notifications to query
            has_been_seen: If the notifications returned should have been seen.
            notification_id: If given, will return the notification which has this id
            skip: Number of notifications to skip (they are ordered by their date of creation,
                first to last).
            user_id: If given, returns the notifications of a specific user
            disable_tqdm: If `True`, the progress bar will be disabled
            as_generator: If `True`, a generator on the notifications is returned.

        Returns:
            A result object which contains the query if it was successful,
                or an error message.
        """

        where = NotificationWhere(
            has_been_seen=has_been_seen,
            notification_id=notification_id,
            user_id=user_id,
        )
        options = QueryOptions(disable_tqdm, first, skip, as_generator)
        return NotificationQuery(self.auth.client)(where, fields, options)

    @typechecked
    def count_notifications(
        self,
        has_been_seen: Optional[bool] = None,
        user_id: Optional[str] = None,
        notification_id: Optional[str] = None,
    ) -> int:
        """Count the number of notifications.

        Args:
            has_been_seen: Filter on notifications that have been seen.
            user_id: Filter on the notifications of a specific user

        Returns:
            The number of notifications with the parameters provided
        """
        where = NotificationWhere(
            has_been_seen=has_been_seen,
            notification_id=notification_id,
            user_id=user_id,
        )
        return NotificationQuery(self.auth.client).count(where)
