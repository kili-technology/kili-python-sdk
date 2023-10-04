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


GQL_COUNT_DATA_INTEGRATIONS = """
    query countDataIntegrations($where: DataIntegrationWhere!) {
      data: countDataIntegrations(where: $where)
    }
    """
