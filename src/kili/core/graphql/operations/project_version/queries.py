"""GraphQL Queries of ProjectVersions."""

from kili.core.graphql.queries import BaseQueryWhere, GraphQLQuery


class ProjectVersionWhere(BaseQueryWhere):
    """Tuple to be passed to the ProjectVersionQuery to restrict query."""

    def __init__(
        self,
        project_id: str,
    ) -> None:
        self.project_id = project_id
        super().__init__()

    def graphql_where_builder(self):
        """Build the GraphQL Where payload sent in the resolver from the SDK ProjectVersionWhere."""
        return {
            "projectId": self.project_id,
        }


class ProjectVersionQuery(GraphQLQuery):
    """ProjectVersion query."""

    @staticmethod
    def query(fragment):
        """Return the GraphQL projects query."""
        return f"""
        query projectVersions($where: ProjectVersionWhere!, $first: PageSize!, $skip: Int!) {{
            data: projectVersions(where: $where, first: $first, skip: $skip) {{
                {fragment}
            }}
        }}
        """

    COUNT_QUERY = """
    query countProjectVersions($where: ProjectVersionWhere!) {
        data: countProjectVersions(where: $where)
    }
    """
