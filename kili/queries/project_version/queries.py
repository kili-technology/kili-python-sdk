"""
Queries of project version queries
"""


def gql_project_version(fragment):
    """
    Return the GraphQL projectVersion query
    """
    return f"""
query ($where: ProjectVersionWhere!, $first: PageSize!, $skip: Int!) {{
  data: projectVersions(where: $where, first: $first, skip: $skip) {{
    {fragment}
  }}
}}
"""


GQL_PROJECT_VERSION_COUNT = """
query($where: ProjectVersionWhere!) {
  data: countProjectVersions(where: $where)
}
"""
