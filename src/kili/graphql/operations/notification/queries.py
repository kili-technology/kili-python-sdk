"""
GraphQL Queries of Notifications
"""


from typing import Optional

from kili.graphql import BaseQueryWhere, GraphQLQuery
from kili.types import Notification


class NotificationWhere(BaseQueryWhere):
    """
    Tuple to be passed to the NotificationQuery to restrict query
    """

    # pylint: disable=too-many-arguments,too-many-locals,too-many-instance-attributes

    def __init__(
        self,
        has_been_seen: Optional[bool] = None,
        notification_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ):
        self.has_been_seen = has_been_seen
        self.notification_id = notification_id
        self.user_id = user_id
        super().__init__()

    def graphql_where_builder(self):
        """Build the GraphQL Where payload sent in the resolver from the SDK NotificationWhere"""
        return {
            "id": self.notification_id,
            "user": {
                "id": self.user_id,
            },
            "hasBeenSeen": self.has_been_seen,
        }


class NotificationQuery(GraphQLQuery):
    """Notification query."""

    FORMAT_TYPE = Notification
    FRAGMENT_TYPE = Notification

    @staticmethod
    def query(fragment):
        """
        Return the GraphQL notifications query
        """

        return f"""
        query notifications($where: NotificationWhere!, $first: PageSize!, $skip: Int!) {{
        data: notifications(where: $where, first: $first, skip: $skip) {{
            {fragment}
        }}
        }}
        """

    COUNT_QUERY = """
query countNotifications($where: NotificationWhere!) {
  data: countNotifications(where: $where)
}
"""
