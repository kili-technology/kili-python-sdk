"""
GraphQL Queries of Project Users
"""


from typing import Optional

from kili.graphql import BaseQueryWhere, GraphQLQuery
from kili.types import ProjectUser


class ProjectUserWhere(BaseQueryWhere):
    """
    Tuple to be passed to the ProjectUserQuery to restrict query
    """

    def __init__(
        self,
        project_id: str,
        email: Optional[str] = None,
        _id: Optional[str] = None,
        organization_id: Optional[str] = None,
    ):
        self.project_id = project_id
        self.email = email
        self._id = _id
        self.organization_id = organization_id
        super().__init__()

    def graphql_where_builder(self):
        """Build the GraphQL Where payload sent in the resolver from the SDK ProjectUserWhere"""
        return {
            "id": self._id,
            "project": {
                "id": self.project_id,
            },
            "user": {
                "email": self.email,
                "organization": {
                    "id": self.organization_id,
                },
            },
        }


class ProjectUserQuery(GraphQLQuery):
    """ProjectUser query."""

    TYPE = ProjectUser

    @staticmethod
    def query(fragment):
        """
        Return the GraphQL projectUsers query
        """
        return f"""
    query projectUsers($where: ProjectUserWhere!, $first: PageSize!, $skip: Int!) {{
    data: projectUsers(where: $where, first: $first, skip: $skip) {{
        {fragment}
    }}
    }}
    """

    COUNT_QUERY = """
    query countProjectUsers($where: ProjectUserWhere!) {
    data: countProjectUsers(where: $where)
    }
    """
