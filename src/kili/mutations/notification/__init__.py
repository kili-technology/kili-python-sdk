"""
Notification mutations
"""

from typeguard import typechecked

from ...helpers import format_result
from .queries import GQL_CREATE_NOTIFICATION, GQL_UPDATE_PROPERTIES_IN_NOTIFICATION


class MutationsNotification:
    """Set of Notification mutations."""

    # pylint: disable=too-many-arguments,too-many-locals

    def __init__(self, auth):
        """Initialize the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

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
                "status": status,
                "url": url,
                "userID": user_id,
            }
        }
        result = self.auth.client.execute(GQL_CREATE_NOTIFICATION, variables)
        return format_result("data", result)

    @typechecked
    def update_properties_in_notification(
        self, notification_id: str, has_been_seen: bool, status: str, url: str
    ):
        """Modify a notification.

        This method is currently only active for Kili administrators.

        Args:
            notification_id :
            hasBeenSeen:
            status :
            url :

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.
        """
        variables = {
            "id": notification_id,
            "hasBeenSeen": has_been_seen,
            "status": status,
            "url": url,
        }
        result = self.auth.client.execute(GQL_UPDATE_PROPERTIES_IN_NOTIFICATION, variables)
        return format_result("data", result)
