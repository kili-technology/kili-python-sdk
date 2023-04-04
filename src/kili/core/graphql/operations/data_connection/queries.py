"""GraphQL Queries of data connections."""


from typing import Optional

from kili.core.graphql import BaseQueryWhere, GraphQLQuery


class DataConnectionsWhere(BaseQueryWhere):
    """Tuple to be passed to the DataConnectionsQuery to restrict the query."""

    def __init__(
        self,
        project_id: Optional[str] = None,
        data_integration_id: Optional[str] = None,
    ) -> None:
        self.project_id = project_id
        self.data_integration_id = data_integration_id
        super().__init__()

    def graphql_where_builder(self):
        # pylint: disable=line-too-long
        """Build the GraphQL Where payload sent in the resolver from the SDK DataConnectionsWhere."""
        return {
            "projectId": self.project_id,
            "integrationId": self.data_integration_id,
        }


class DataConnectionsQuery(GraphQLQuery):
    """DataConnections query."""

    @staticmethod
    def query(fragment):
        """Return the GraphQL dataConnections query."""
        return f"""
        query dataConnections($where: DataConnectionsWhere!, $first: PageSize!, $skip: Int!) {{
          data: dataConnections(where: $where, first: $first, skip: $skip) {{
            {fragment}
          }}
        }}
        """


class DataConnectionIdWhere(BaseQueryWhere):
    """Tuple to be passed to the DataConnectionQuery to restrict the query."""

    def __init__(
        self,
        data_connection_id: str,
    ) -> None:
        self.data_connection_id = data_connection_id
        super().__init__()

    def graphql_where_builder(self):
        """Build the GraphQL Where payload sent in the resolver from the SDK DataConnectionWhere."""
        return {
            "id": self.data_connection_id,
        }


class DataConnectionQuery(GraphQLQuery):
    """DataConnection query."""

    @staticmethod
    def query(fragment):
        """Return the GraphQL dataConnection query."""
        return f"""
        query dataConnection($where: DataConnectionIdWhere!) {{
          data: dataConnection(where: $where) {{
            {fragment}
          }}
        }}
        """
