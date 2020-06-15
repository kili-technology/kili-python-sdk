def gql_projects(fragment: str):
    return(f'''
query($where: ProjectWhere!, $first: PageSize!, $skip: Int!) {{
  data: projects(where: $where, first: $first, skip: $skip) {{
    {fragment}
  }}
}}
''')

GQL_PROJECTS_COUNT = f'''
query($where: ProjectWhere!) {{
  data: countProjects(where: $where)
}}
'''