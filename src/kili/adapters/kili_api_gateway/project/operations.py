"""GraphQL Project operations."""


def get_project_query(fragment: str) -> str:
    """Return the GraphQL projects query."""
    return f"""
        query projects($where: ProjectWhere!, $first: PageSize!, $skip: Int!) {{
            data: projects(where: $where, first: $first, skip: $skip) {{
                {fragment}
            }}
        }}
        """
