"""GraphQL Queries of data integrations."""


from typing import Optional

from kili.core.graphql import BaseQueryWhere, GraphQLQuery


class DataIntegrationWhere(BaseQueryWhere):
    """Tuple to be passed to the DataIntegrationsQuery to restrict the query."""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        data_integration_id: Optional[str] = None,
        name: Optional[str] = None,
        platform: Optional[str] = None,
        status: Optional[str] = None,
        organization_id: Optional[str] = None,
    ) -> None:
        self.data_integration_id = data_integration_id
        self.name = name
        self.platform = platform
        self.status = status
        self.organization_id = organization_id
        super().__init__()

    def graphql_where_builder(self):
        # pylint: disable=line-too-long
        """Build the GraphQL Where payload sent in the resolver from the SDK DataIntegrationWhere."""
        return {
            "id": self.data_integration_id,
            "name": self.name,
            "platform": self.platform,
            "status": self.status,
            "organizationId": self.organization_id,
        }


class DataIntegrationsQuery(GraphQLQuery):
    """DataIntegrations query."""

    @staticmethod
    def query(fragment):
        """Return the GraphQL dataIntegrations query."""
        return f"""
        query dataIntegrations($where: DataIntegrationWhere!, $first: PageSize!, $skip: Int!) {{
          data: dataIntegrations(where: $where, skip: $skip, first: $first) {{
            {fragment}
          }}
        }}
        """

    COUNT_QUERY = """
    query countDataIntegrations($where: DataIntegrationWhere!) {
      data: countDataIntegrations(where: $where)
    }
    """
