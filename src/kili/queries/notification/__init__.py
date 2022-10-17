"""Notification queries."""

from typing import Generator, List, Optional, Union

from typeguard import typechecked

from ...helpers import format_result, fragment_builder
from ...types import Notification
from ...utils.pagination import row_generator_from_paginated_calls
from .queries import GQL_NOTIFICATIONS_COUNT, gql_notifications


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
    ) -> Union[List[dict], Generator[dict, None, None]]:
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

        count_args = {"has_been_seen": has_been_seen, "user_id": user_id}
        disable_tqdm = disable_tqdm or as_generator or notification_id is not None
        payload_query = {
            "where": {
                "id": notification_id,
                "user": {
                    "id": user_id,
                },
                "hasBeenSeen": has_been_seen,
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
            disable_tqdm,
        )

        if as_generator:
            return notifications_generator
        return list(notifications_generator)

    def _query_notifications(self, skip: int, first: int, payload: dict, fields: List[str]):
        payload.update({"skip": skip, "first": first})
        _gql_notifications = gql_notifications(fragment_builder(fields, Notification))
        result = self.auth.client.execute(_gql_notifications, payload)
        return format_result("data", result)

    @typechecked
    def count_notifications(
        self, has_been_seen: Optional[bool] = None, user_id: Optional[str] = None
    ) -> int:
        """Count the number of notifications.

        Args:
            has_been_seen: Filter on notifications that have been seen.
            user_id: Filter on the notifications of a specific user

        Returns:
            The number of notifications with the parameters provided
        """
        variables = {
            "where": {
                "user": {
                    "id": user_id,
                },
                "hasBeenSeen": has_been_seen,
            },
        }
        result = self.auth.client.execute(GQL_NOTIFICATIONS_COUNT, variables)
        return format_result("data", result, int)
