"""GraphQL Queries of Users."""


from typing import Optional

from kili.core.graphql.queries import BaseQueryWhere, GraphQLQuery


class UserWhere(BaseQueryWhere):
    """Tuple to be passed to the UserQuery to restrict query."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        email: Optional[str] = None,
        organization_id: Optional[str] = None,
    ) -> None:
        self.api_key = api_key
        self.email = email
        self.organization_id = organization_id
        super().__init__()

    def graphql_where_builder(self):
        """Build the GraphQL Where payload sent in the resolver from the SDK UserWhere."""
        return {
            "apiKey": self.api_key,
            "email": self.email,
            "organization": {"id": self.organization_id},
        }


class UserQuery(GraphQLQuery):
    """User query."""

    @staticmethod
    def query(fragment):
        """Return the GraphQL users query."""
        return f"""
        query users($where: UserWhere!, $first: PageSize!, $skip: Int!) {{
            data: users(where: $where, first: $first, skip: $skip) {{
                {fragment}
            }}
        }}
        """

    COUNT_QUERY = """
    query countUsers($where: UserWhere!) {
        data: countUsers(where: $where)
    }
    """


GQL_ME = """
query Me {
    data: me {
        id
        email
    }
}
"""
