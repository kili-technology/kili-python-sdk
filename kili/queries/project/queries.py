
def gql_projects(fragment: str):
    return(f'''
query($where: ProjectWhere!, $first: PageSize!, $skip: Int!) {{
  data: projects(where: $where, first: $first, skip: $skip) {{
    {fragment}
  }}
}}
''')
