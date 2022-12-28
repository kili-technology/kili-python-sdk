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


GQL_COUNT_PROJECT_USERS = """
query countProjectUsers($where: ProjectUserWhere!) {
  data: countProjectUsers(where: $where)
}
"""


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


ProjectUserQuery = GraphQLQuery(
    _type=ProjectUser,
    query=query,
    count_query=GQL_COUNT_PROJECT_USERS,
    where_payload_builder=where_payload_builder,
)
