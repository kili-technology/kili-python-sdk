from .fragments import USER_FRAGMENT

GQL_USERS = f'''
query($where: UserWhere!) {{
  data: users(where: $where) {{
    {USER_FRAGMENT}
  }}
}}
'''
