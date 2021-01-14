def gql_notifications(fragment):
    return (f'''
query ($where: NotificationWhere!, $first: PageSize!, $skip: Int!) {{
  data: notifications(where: $where, first: $first, skip: $skip) {{
    {fragment}
  }}
}}
''')


GQL_NOTIFICATIONS_COUNT = f'''
query($where: NotificationWhere!) {{
  data: countNotifications(where: $where)
}}
'''
