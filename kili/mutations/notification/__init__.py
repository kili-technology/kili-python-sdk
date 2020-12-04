from ...helpers import Compatible, format_result
from .queries import (GQL_CREATE_NOTIFICATION,
                      GQL_UPDATE_PROPERTIES_IN_NOTIFICATION)


class MutationsNotification:

    def __init__(self, auth):
        """
        Initializes the subclass

        Parameters
        ----------
        - auth : KiliAuth object
        """
        self.auth = auth

    @Compatible(['v1', 'v2'])
    def create_notification(self, message: str, status: str, url: str, user_id: str):
        """
        Create a notification

        This method is currently only active for Kili administrators.

        Parameters
        ----------
        - message : str
        - status : str
        - url : str
        - user_id : str

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.
        """
        variables = {
            'data': {
                'message': message,
                'status': status,
                'url': url,
                'userID': user_id
            }
        }
        result = self.auth.client.execute(GQL_CREATE_NOTIFICATION, variables)
        return format_result('data', result)

    @Compatible(['v1', 'v2'])
    def update_properties_in_notification(self, notification_id: str, has_been_seen: bool, status: str, url: str):
        """
        Modify a notification

        This method is currently only active for Kili administrators.

        Parameters
        ----------
        - notification_id : str
        - hasBeenSeen: bool
        - status : str
        - url : str

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.
        """
        variables = {
            'id': notification_id,
            'hasBeenSeen': has_been_seen,
            'status': status,
            'url': url
        }
        result = self.auth.client.execute(
            GQL_UPDATE_PROPERTIES_IN_NOTIFICATION, variables)
        return format_result('data', result)
