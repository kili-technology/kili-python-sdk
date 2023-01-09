"""
GraphQL Queries of Projects
"""


from typing import Optional

from kili.graphql import BaseQueryWhere, GraphQLQuery
from kili.types import Project


class ProjectWhere(BaseQueryWhere):
    """
    Tuple to be passed to the ProjectQuery to restrict query
    """

    # pylint: disable=too-many-arguments,too-many-locals,too-many-instance-attributes

    def __init__(
        self,
        project_id: Optional[str] = None,
        search_query: Optional[str] = None,
        should_relaunch_kpi_computation: Optional[bool] = None,
        updated_at_gte: Optional[str] = None,
        updated_at_lte: Optional[str] = None,
    ):
        self.project_id = project_id
        self.search_query = search_query
        self.should_relaunch_kpi_computation = should_relaunch_kpi_computation
        self.updated_at_gte = updated_at_gte
        self.updated_at_lte = updated_at_lte
        super().__init__()

    def graphql_where_builder(self):
        """Build the GraphQL Where payload sent in the resolver from the SDK ProjectWhere"""
        return {
            "id": self.project_id,
            "searchQuery": self.search_query,
            "shouldRelaunchKpiComputation": self.should_relaunch_kpi_computation,
            "updatedAtGte": self.updated_at_gte,
            "updatedAtLte": self.updated_at_lte,
        }


class ProjectQuery(GraphQLQuery):
    """Project query."""

    TYPE = Project

    @staticmethod
    def query(fragment):
        """
        Return the GraphQL projects query
        """
        return f"""
    query projects($where: ProjectWhere!, $first: PageSize!, $skip: Int!) {{
    data: projects(where: $where, first: $first, skip: $skip) {{
        {fragment}
    }}
    }}
    """

    COUNT_QUERY = """
    query countProjects($where: ProjectWhere!) {
    data: countProjects(where: $where)
    }
    """
