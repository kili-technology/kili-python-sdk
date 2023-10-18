"""GraphQL Queries of Project Users."""

from typing import Literal, Optional

from kili.core.graphql.queries import BaseQueryWhere, GraphQLQuery


class ProjectUserWhere(BaseQueryWhere):
    """Tuple to be passed to the ProjectUserQuery to restrict query."""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        project_id: str,
        email: Optional[str] = None,
        _id: Optional[str] = None,
        organization_id: Optional[str] = None,
        status: Optional[Literal["ACTIVATED", "ORG_ADMIN", "ORG_SUSPENDED"]] = None,
        active_in_project: Optional[bool] = None,
    ) -> None:
        self.project_id = project_id
        self.email = email
        self._id = _id
        self.organization_id = organization_id
        self.status = status
        self.active_in_project = active_in_project  # user not deleted and nbr of labeled assets > 0
        super().__init__()

    def graphql_where_builder(self):
        """Build the GraphQL Where payload sent in the resolver from the SDK ProjectUserWhere."""
        return {
            "id": self._id,
            "status": self.status,
            "activeInProject": self.active_in_project,
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

    @staticmethod
    def query(fragment) -> str:
        """Return the GraphQL projectUsers query."""
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
