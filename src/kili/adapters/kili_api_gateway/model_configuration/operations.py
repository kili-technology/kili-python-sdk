"""GraphQL Asset operations."""


def get_organization_models_query(fragment: str) -> str:
    """Return the GraphQL projectModels query."""
    return f"""
          query Models($where: ModelWhere!, $first: PageSize!, $skip: Int!) {{
            data: models(where: $where, first: $first, skip: $skip) {{
                {fragment}
              }}
            }}
        """


def get_create_model_mutation(fragment: str) -> str:
    """Return the GraphQL createProjectModel mutation."""
    return f"""
          mutation CreateModel($input: CreateModelInput!) {{
            createModel(input: $input) {{
              {fragment}
            }}
          }}
        """


def get_delete_model_mutation() -> str:
    """Return the GraphQL deleteOrganizationModel mutation."""
    return """
    mutation DeleteModel($deleteModelId: ID!) {
        deleteModel(id: $deleteModelId)
    }
    """


def get_create_project_model_mutation(fragment: str) -> str:
    """Return the GraphQL createProjectModel mutation."""
    return f"""
          mutation CreateProjectModel($input: CreateProjectModelInput!) {{
            createProjectModel(input: $input) {{
              {fragment}
            }}
          }}
        """


def get_project_models_query(fragment: str) -> str:
    """Return the GraphQL projectModels query."""
    return f"""
        query ProjectModels($where: ProjectModelWhere!, $first: PageSize!, $skip: Int!) {{
          data: projectModels(where: $where, first: $first, skip: $skip) {{
            {fragment}
          }}
        }}
        """
