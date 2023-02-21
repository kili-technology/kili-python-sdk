"""
GraphQL Queries of data connections
"""


from typing import Optional

from kili.graphql import BaseQueryWhere, GraphQLQuery


class DataConnectionsWhere(BaseQueryWhere):
    """
    Tuple to be passed to the DataConnectionsQuery to restrict the query
    """

    def __init__(
        self,
        project_id: Optional[str] = None,
        integration_id: Optional[str] = None,
    ) -> None:
        self.project_id = project_id
        self.integration_id = integration_id
        super().__init__()

    def graphql_where_builder(self):
        """Build the GraphQL Where payload sent in the resolver from the SDK DataConnectionsWhere"""
        return {
            "projectId": self.project_id,
            "integrationId": self.integration_id,
        }


class DataConnectionsQuery(GraphQLQuery):
    """DataConnections query."""

    @staticmethod
    def query(fragment):
        """
        Return the GraphQL dataConnections query
        """
        return f"""
        query dataConnections(where: DataConnectionsWhere!, first: PageSize!, skip: Int!) {{
          data: dataConnections(where: $where, skip: $skip, first: $first) {{
            {fragment}
          }}
        }}
        """
