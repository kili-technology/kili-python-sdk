"""Client presentation methods for notifications."""

from typing import Dict, Generator, Iterable, List, Literal, Optional, overload

from typeguard import typechecked

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.domain.notification import NotificationFilter, NotificationId
from kili.domain.types import ListOrTuple
from kili.domain.user import UserFilter, UserId
from kili.presentation.client.helpers.common_validators import (
    disable_tqdm_if_as_generator,
)
from kili.use_cases.notification import NotificationUseCases
from kili.utils.logcontext import for_all_methods, log_call

from .base import BaseClientMethods


@for_all_methods(log_call, exclude=["__init__"])
class NotificationClientMethods(BaseClientMethods):
    """Methods attached to the Kili client, to run actions on notifications."""

    @overload
    def notifications(
        self,
        fields: ListOrTuple[str] = (
            "createdAt",
            "hasBeenSeen",
            "id",
            "message",
            "status",
            "userID",
        ),
        first: Optional[int] = None,
        has_been_seen: Optional[bool] = None,
        notification_id: Optional[str] = None,
        skip: int = 0,
        user_id: Optional[str] = None,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: Literal[True],
    ) -> Generator[Dict, None, None]:
        ...

    @overload
    def notifications(
        self,
        fields: ListOrTuple[str] = (
            "createdAt",
            "hasBeenSeen",
            "id",
            "message",
            "status",
            "userID",
        ),
        first: Optional[int] = None,
        has_been_seen: Optional[bool] = None,
        notification_id: Optional[str] = None,
        skip: int = 0,
        user_id: Optional[str] = None,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: Literal[False] = False,
    ) -> List[Dict]:
        ...

    @typechecked
    def notifications(
        self,
        fields: ListOrTuple[str] = (
            "createdAt",
            "hasBeenSeen",
            "id",
            "message",
            "status",
            "userID",
        ),
        first: Optional[int] = None,
        has_been_seen: Optional[bool] = None,
        notification_id: Optional[str] = None,
        skip: int = 0,
        user_id: Optional[str] = None,
        disable_tqdm: Optional[bool] = None,
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
        disable_tqdm = disable_tqdm_if_as_generator(as_generator, disable_tqdm)
        options = QueryOptions(disable_tqdm, first, skip)
        filters = NotificationFilter(
            has_been_seen=has_been_seen,
            id=NotificationId(notification_id) if notification_id else None,
            user=UserFilter(id=UserId(user_id)) if user_id else None,
        )
        notifications_gen = NotificationUseCases(self.kili_api_gateway).list_notifications(
            options=options, fields=fields, filters=filters
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
        filters = NotificationFilter(
            has_been_seen=has_been_seen,
            id=NotificationId(notification_id) if notification_id else None,
            user=UserFilter(id=UserId(user_id)) if user_id else None,
        )
        return NotificationUseCases(self.kili_api_gateway).count_notifications(filters=filters)
