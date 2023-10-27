"""Collection of notification's related GraphQL queries and mutations."""

GQL_COUNT_NOTIFICATIONS = """
    query countNotifications($where: NotificationWhere!) {
        data: countNotifications(where: $where)
    }
    """


def get_notifications_query(fragment: str) -> str:
    """Get the query for notifications."""
    return f"""
        query notifications($where: NotificationWhere!, $first: PageSize!, $skip: Int!) {{
            data: notifications(where: $where, first: $first, skip: $skip) {{
                {fragment}
            }}
        }}
        """
