"""
Queries of notification queries
"""


def gql_notifications(fragment):
    """
    Return the GraphQL notifications query
    """
    return f"""
query ($where: NotificationWhere!, $first: PageSize!, $skip: Int!) {{
  data: notifications(where: $where, first: $first, skip: $skip) {{
    {fragment}
  }}
}}
"""


GQL_NOTIFICATIONS_COUNT = """
query($where: NotificationWhere!) {
  data: countNotifications(where: $where)
}
"""
