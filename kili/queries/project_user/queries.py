from .fragments import PROJECT_USER_FRAGMENT, PROJECT_USER_FRAGMENT_WITH_KPIS

GQL_PROJECT_USERS = f'''
query($where: ProjectUserWhere!, $first: PageSize!, $skip: Int!) {{
  data: projectUsers(where: $where, first: $first, skip: $skip) {{
    {PROJECT_USER_FRAGMENT}
  }}
}}
'''

GQL_PROJECT_USERS_WITH_KPIS = f'''
query($where: ProjectUserWhere!, $first: PageSize!, $skip: Int!) {{
  data: projectUsers(where: $where, first: $first, skip: $skip) {{
    {PROJECT_USER_FRAGMENT_WITH_KPIS}
  }}
}}
'''
