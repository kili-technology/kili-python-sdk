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


def get_update_properties_in_project_mutation(fragment: str) -> str:
    """Return the GraphQL updatePropertiesInProject mutation."""
    return f"""
        mutation updatePropertiesInProject($data: ProjectData!, $where: ProjectWhere!) {{
            data: updatePropertiesInProject(data: $data, where: $where) {{
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
