"""
GraphQL Queries of Project Users
"""


from typing import NamedTuple, Optional

from kili.graphql import GraphQLQuery
from kili.types import ProjectUser


class ProjectUserWhere(NamedTuple):
    """
    Tuple to be passed to the ProjectUserQuery to restrict query
    """

    project_id: str
    email: Optional[str] = None
    id: Optional[str] = None
    organization_id: Optional[str] = None


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

    @staticmethod
    def where_payload_builder(where: ProjectUserWhere):
        """Build the GraphQL Where payload sent in the resolver from the SDK ProjectUserWhere"""
        return {
            "id": where.id,
            "project": {
                "id": where.project_id,
            },
            "user": {
                "email": where.email,
                "organization": {
                    "id": where.organization_id,
                },
            },
        }
