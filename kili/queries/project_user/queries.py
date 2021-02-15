def gql_project_users(fragment):
    return(f'''
query($where: ProjectUserWhere!, $first: PageSize!, $skip: Int!) {{
  data: projectUsers(where: $where, first: $first, skip: $skip) {{
    {fragment}
  }}
}}
''')


GQL_PROJECT_USERS_COUNT = f'''
query($where: ProjectUserWhere!) {{
  data: countProjectUsers(where: $where)
}}
'''