"""GraphQL Cloud Storage operations."""


def get_list_data_integrations_query(fragment: str) -> str:
    """Return the GraphQL query to list data integrations."""
    return f"""
        query dataIntegrations($where: DataIntegrationWhere!, $first: PageSize!, $skip: Int!) {{
          data: dataIntegrations(where: $where, skip: $skip, first: $first) {{
            {fragment}
          }}
        }}
        """


def get_list_data_connections_query(fragment: str) -> str:
    """Return the GraphQL query to list data connections."""
    return f"""
        query dataConnections($where: DataConnectionsWhere!, $first: PageSize!, $skip: Int!) {{
          data: dataConnections(where: $where, first: $first, skip: $skip) {{
            {fragment}
          }}
        }}
        """


def get_data_connection_query(fragment: str) -> str:
    """Return the GraphQL query to get a data connection."""
    return f"""
        query dataConnection($where: DataConnectionIdWhere!) {{
          data: dataConnection(where: $where) {{
            {fragment}
          }}
        }}
        """


def get_add_data_connection_mutation(fragment: str) -> str:
    """Return the GraphQL mutation to add a data connection."""
    return f"""
    mutation addDataConnection($data: DataConnectionInput!) {{
      data: addDataConnection(data: $data) {{
        {fragment}
      }}
    }}
    """


def get_compute_data_connection_differences_mutation(fragment: str) -> str:
    """Return the GraphQL mutation to compute data connection differences."""
    return f"""
    mutation computeDifferences(
        $where: DataConnectionIdWhere!,
        $data: DataConnectionComputeDifferencesPayload
      ) {{
          data: computeDifferences(where: $where, data: $data) {{
              {fragment}
          }}
      }}
    """


def get_validate_data_connection_differences_mutation(fragment: str) -> str:
    """Return the GraphQL mutation to validate data connection differences."""
    return f"""
    mutation validateDataDifferences(
      $where: ValidateDataDifferencesWhere!,
      $processingParameters: String) {{
      data: validateDataDifferences(
        where: $where,
        processingParameters: $processingParameters
      ) {{
        {fragment}
      }}
    }}
    """


GQL_COUNT_DATA_INTEGRATIONS = """
    query countDataIntegrations($where: DataIntegrationWhere!) {
      data: countDataIntegrations(where: $where)
    }
    """


def get_update_integration_mutation(fragment: str) -> str:
    """Return the GraphQL mutation to update a data integrations."""
    return f"""
    mutation UpdatePropertiesInDataIntegration(
      $data: DataIntegrationData!,
      $where: DataIntegrationWhere!) {{
      data: updatePropertiesInDataIntegration(data: $data, where: $where) {{
        {fragment}
      }}
    }}
    """


def get_create_integration_mutation(fragment: str) -> str:
    """Return the GraphQL mutation to create a data integration."""
    return f"""
        mutation CreateDataIntegration($data: DataIntegrationData!) {{
          data: createDataIntegration(data: $data) {{
            {fragment}
          }}
        }}
        """


GQL_DELETE_DATA_INTEGRATION = """
    mutation DeleteDataIntegration($where: DataIntegrationWhere!) {
            data: deleteDataIntegration(where: $where)
        }
    """
