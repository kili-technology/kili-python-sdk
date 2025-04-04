"""Notification mutations."""
from typing import Optional, Union

from typeguard import typechecked

from kili.core.graphql.graphql_client import GraphQLClient
from kili.entrypoints.base import BaseOperationEntrypointMixin
from kili.utils.logcontext import for_all_methods, log_call

from .queries import GQL_CREATE_NOTIFICATION, GQL_UPDATE_PROPERTIES_IN_NOTIFICATION


@for_all_methods(log_call, exclude=["__init__"])
class MutationsNotification(BaseOperationEntrypointMixin):
    """Set of Notification mutations."""

    graphql_client: GraphQLClient

    @typechecked
    def create_notification(self, message: str, status: str, url: str, user_id: str):
        """Create a notification.

        This method is currently only active for Kili administrators.

        Args:
            message :
            status :
            url :
            user_id :

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.
        """
        variables = {
            "data": {
                "message": message,
                "progress": None,
                "status": status,
                "url": url,
                "userID": user_id,
            }
        }
        result = self.graphql_client.execute(GQL_CREATE_NOTIFICATION, variables)
        return self.format_result("data", result)

    @typechecked
    def update_properties_in_notification(
        self,
        notification_id: str,
        has_been_seen: Union[bool, None],
        status: str,
        url: str,
        progress: Optional[int] = None,
        task_id: Optional[str] = None,
    ):
        """Modify a notification.

        This method is currently only active for Kili administrators.

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.
        """
        variables = {
            "id": notification_id,
            "hasBeenSeen": has_been_seen,
            "progress": progress,
            "status": status,
            "taskId": task_id,
            "url": url,
        }
        result = self.graphql_client.execute(GQL_UPDATE_PROPERTIES_IN_NOTIFICATION, variables)
        return self.format_result("data", result)
