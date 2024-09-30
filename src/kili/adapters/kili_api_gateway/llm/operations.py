"""GraphQL Asset operations."""


def get_models_query(fragment: str) -> str:
    """Return the GraphQL projectModels query."""
    return f"""
          query Models($where: ModelWhere!, $first: PageSize!, $skip: Int!) {{
            data: models(where: $where, first: $first, skip: $skip) {{
                {fragment}
              }}
            }}
        """


def get_model_query(fragment: str) -> str:
    """Return the GraphQL model query by ID."""
    return f"""
        query Model($modelId: ID!) {{
            model(id: $modelId) {{
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


def get_update_model_mutation(fragment: str) -> str:
    """Return the GraphQL updateModel mutation."""
    return f"""
        mutation UpdateModel($id: ID!, $input: UpdateModelInput!) {{
            updateModel(id: $id, input: $input) {{
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


def get_update_project_model_mutation(fragment: str) -> str:
    """Return the GraphQL updateProjectModel mutation."""
    return f"""
        mutation UpdateProjectModel($updateProjectModelId: ID!, $input: UpdateProjectModelInput!) {{
            updateProjectModel(id: $updateProjectModelId, input: $input) {{
                {fragment}
            }}
        }}
    """


def get_delete_project_model_mutation() -> str:
    """Return the GraphQL deleteProjectModel mutation."""
    return """
    mutation DeleteProjectModel($deleteProjectModelId: ID!) {
       deleteProjectModel(id: $deleteProjectModelId)
    }
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


def get_create_llm_asset_mutation(fragment: str) -> str:
    """Return the GraphQL createLLMAsset mutation."""
    return f"""
        mutation CreateLLMAsset($where: ProjectWhere!, $data: CreateLLMAssetData!) {{
            createLLMAsset(where: $where, data: $data) {{
                {fragment}
            }}
        }}
    """


def get_create_chat_item_mutation(fragment: str) -> str:
    """Return the GraphQL createChatItem mutation."""
    return f"""
        mutation CreateChatItem($data: CreateChatItemData!, $where: AssetWhere!) {{
            createChatItem(data: $data, where: $where) {{
                {fragment}
            }}
        }}
    """
