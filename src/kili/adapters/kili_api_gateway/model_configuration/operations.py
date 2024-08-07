"""GraphQL Asset operations."""


def get_project_models_query(fragment: str) -> str:
    """Return the GraphQL projectModels query."""
    return f"""
        query ProjectModels($where: ProjectModelWhere!, $first: PageSize!, $skip: Int!) {{
          data: projectModels(where: $where, first: $first, skip: $skip) {{
            {fragment}
          }}
        }}
        """
