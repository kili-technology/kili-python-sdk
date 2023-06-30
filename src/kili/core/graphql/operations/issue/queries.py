"""GraphQL Queries of Issues."""

from typing import List, Literal, Optional

from kili.core.graphql import BaseQueryWhere, GraphQLQuery


class IssueWhere(BaseQueryWhere):
    """Tuple to be passed to the IssueQuery to restrict query."""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        project_id: Optional[str] = None,
        asset_id: Optional[str] = None,
        asset_id_in: Optional[List[str]] = None,
        issue_type: Optional[Literal["QUESTION", "ISSUE"]] = None,
        status: Optional[Literal["OPEN", "SOLVED"]] = None,
    ):
        self.project_id = project_id
        self.asset_id = asset_id
        self.asset_id_in = asset_id_in
        self.issue_type = issue_type
        self.status = status
        super().__init__()

    def graphql_where_builder(self):
        """Build the GraphQL Where payload sent in the resolver from the SDK IssueWhere."""
        return {
            "project": {"id": self.project_id},
            "asset": {"id": self.asset_id},
            "assetIn": self.asset_id_in,
            "status": self.status,
            "type": self.issue_type,
        }


class IssueQuery(GraphQLQuery):
    """Issue query."""

    @staticmethod
    def query(fragment):
        """Return the GraphQL issues query."""
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
