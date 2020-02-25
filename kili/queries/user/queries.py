from .fragments import USER_FRAGMENT

GQL_GET_USER = f'''
query($email: String!) {{
  data: getUser(email: $email) {{
    {USER_FRAGMENT}
  }}
}}
'''
