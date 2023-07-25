"""Notification queries."""

from typing import Dict, Generator, Iterable, List, Literal, Optional, overload

from typeguard import typechecked

from kili.core.graphql import QueryOptions
from kili.core.graphql.operations.notification.queries import (
    NotificationQuery,
    NotificationWhere,
)
from kili.core.helpers import disable_tqdm_if_as_generator
from kili.entrypoints.base import BaseOperationEntrypointMixin
from kili.utils.logcontext import for_all_methods, log_call


@for_all_methods(log_call, exclude=["__init__"])
class QueriesNotification(BaseOperationEntrypointMixin):
    """Set of Notification queries."""

    # pylint: disable=too-many-arguments,dangerous-default-value

    @overload
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
        *,
        as_generator: Literal[True],
    ) -> Generator[Dict, None, None]:
        ...

    @overload
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
        *,
        as_generator: Literal[False] = False,
    ) -> List[Dict]:
        ...

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
        *,
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
            An iterable of notifications.
        """
        where = NotificationWhere(
            has_been_seen=has_been_seen,
            notification_id=notification_id,
            user_id=user_id,
        )
        disable_tqdm = disable_tqdm_if_as_generator(as_generator, disable_tqdm)
        options = QueryOptions(disable_tqdm, first, skip)
        notifications_gen = NotificationQuery(self.graphql_client, self.http_client)(
            where, fields, options
        )

        if as_generator:
            return notifications_gen
        return list(notifications_gen)

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
            user_id: Filter on the notifications of a specific user.
            notification_id: Filter on a specific notification.

        Returns:
            The number of notifications with the parameters provided
        """
        where = NotificationWhere(
            has_been_seen=has_been_seen,
            notification_id=notification_id,
            user_id=user_id,
        )
        return NotificationQuery(self.graphql_client, self.http_client).count(where)
