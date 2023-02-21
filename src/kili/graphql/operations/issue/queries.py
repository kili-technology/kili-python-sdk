"""
GraphQL Queries of Issues
"""

from kili.graphql import BaseQueryWhere, GraphQLQuery


class IssueWhere(BaseQueryWhere):
    """
    Tuple to be passed to the IssueQuery to restrict query
    """

    def __init__(
        self,
        project_id: str,
    ):
        self.project_id = project_id
        super().__init__()

    def graphql_where_builder(self):
        """Build the GraphQL Where payload sent in the resolver from the SDK IssueWhere"""
        return {"project": {"id": self.project_id}}


class IssueQuery(GraphQLQuery):
    """Issue query."""

    @staticmethod
    def query(fragment):
        """
        Return the GraphQL issues query
        """
        return f"""
        query issues($where: IssueWhere!, $first: PageSize!, $skip: Int!) {{
            data: issues(where: $where, first: $first, skip: $skip) {{
                {fragment}
            }}
        }}
        """

    COUNT_QUERY = """
    query countIssues($where: IssueWhere!) {
        data: countIssues(where: $where)
    }
    """
