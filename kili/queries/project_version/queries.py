def gql_project_version(fragment):
    return f'''
query ($where: ProjectVersionWhere!, $first: PageSize!, $skip: Int!) {{
  data: projectVersions(where: $where, first: $first, skip: $skip) {{
    {fragment}
  }}
}}
'''


GQL_PROJECT_VERSION_COUNT = f'''
query($where: ProjectVersionWhere!) {{
  data: countProjectVersions(where: $where)
}}
'''
