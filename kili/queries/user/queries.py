from .fragments import USER_FRAGMENT

GQL_USERS = f'''
query($where: UserWhere!, $first: PageSize!, $skip: Int!) {{
  data: users(where: $where, first: $first, skip: $skip) {{
    {USER_FRAGMENT}
  }}
}}
'''
