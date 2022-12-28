"""
Queries of project user queries
"""


from typing import NamedTuple, Optional

from kili.graphql import GraphQLQuery
from kili.types import ProjectUser


def query(fragment):
    """
    Return the GraphQL projectUsers query
    """
    return f"""
query($where: ProjectUserWhere!, $first: PageSize!, $skip: Int!) {{
  data: projectUsers(where: $where, first: $first, skip: $skip) {{
    {fragment}
  }}
}}
"""


count_query = """
query($where: ProjectUserWhere!) {
  data: countProjectUsers(where: $where)
}
"""


class ProjectUserWhere(NamedTuple):
    project_id: str
    email: Optional[str] = None
    id: Optional[str] = None
    organization_id: Optional[str] = None


def where_payload_builder(where: ProjectUserWhere):
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
    count_query=count_query,
    where_payload_builder=where_payload_builder,
)
