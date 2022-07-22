"""
Queries of project queries
"""


def gql_projects(fragment: str):
    """
    Return the GraphQL projects query
    """
    return f"""
query($where: ProjectWhere!, $first: PageSize!, $skip: Int!) {{
  data: projects(where: $where, first: $first, skip: $skip) {{
    {fragment}
  }}
}}
"""


GQL_PROJECTS_COUNT = """
query($where: ProjectWhere!) {
  data: countProjects(where: $where)
}
"""
