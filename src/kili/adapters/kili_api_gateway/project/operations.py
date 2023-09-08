"""GraphQL Project operations."""


def get_projects_query(fragment: str) -> str:
    """Return the GraphQL projects query."""
    return f"""
        query projects($where: ProjectWhere!, $first: PageSize!, $skip: Int!) {{
            data: projects(where: $where, first: $first, skip: $skip) {{
                {fragment}
            }}
        }}
        """


GQL_COUNT_PROJECTS = """
query countProjects($where: ProjectWhere!) {
    data: countProjects(where: $where)
}
"""

GQL_CREATE_PROJECT = """
mutation($data: CreateProjectData!) {
    data: createProject(data: $data) {
        id
    }
}
"""
