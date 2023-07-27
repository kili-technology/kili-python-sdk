"""GraphQL Queries of Organizations."""


from datetime import datetime
from typing import Dict, Optional

from kili.core.graphql import BaseQueryWhere, GraphQLQuery


class OrganizationWhere(BaseQueryWhere):
    """Tuple to be passed to the OrganizationQuery to restrict query."""

    def __init__(
        self,
        email: Optional[str] = None,
        organization_id: Optional[str] = None,
    ):
        self.email = email
        self.organization_id = organization_id
        super().__init__()

    def graphql_where_builder(self):
        """Build the GraphQL Where payload sent in the resolver from the SDK OrganizationWhere."""
        return {
            "id": self.organization_id,
            "user": {
                "email": self.email,
            },
        }


class OrganizationMetricsWhere(BaseQueryWhere):
    """Tuple to be passed to the OrganizationQuery to restrict query."""

    def __init__(
        self,
        organization_id: str,
        start_date: datetime,
        end_date: datetime,
    ):
        self.organization_id = organization_id
        self.start_date = start_date
        self.end_date = end_date
        super().__init__()

    def graphql_where_builder(self):
        """Build the GraphQL Where payload sent in the resolver from the SDK OrganizationWhere."""
        return {
            "organizationId": self.organization_id,
            "startDate": self.start_date.isoformat(sep="T", timespec="milliseconds") + "Z",
            "endDate": self.end_date.isoformat(sep="T", timespec="milliseconds") + "Z",
        }


class OrganizationQuery(GraphQLQuery):
    """Organization query."""

    @staticmethod
    def query(fragment):
        """Return the GraphQL organizations query."""
        return f"""
        query organizations($where: OrganizationWhere!, $first: PageSize!, $skip: Int!) {{
            data: organizations(where: $where, first: $first, skip: $skip) {{
                {fragment}
            }}
        }}
        """

    COUNT_QUERY = """
    query countOrganizations($where: OrganizationWhere!) {
        data: countOrganizations(where: $where)
    }
    """

    GQL_ORGANIZATION_METRICS = """
    query organizationMetrics($where: OrganizationMetricsWhere!) {
        data: organizationMetrics(where: $where) {
            numberOfAnnotations
            numberOfHours
            numberOfLabeledAssets
        }
    }
    """

    def metrics(self, where: OrganizationMetricsWhere) -> Dict:
        """Execute the organizationMetrics operation."""
        payload = {"where": where.graphql_payload}
        result = self.client.execute(self.GQL_ORGANIZATION_METRICS, payload)
        return self.format_result("data", result)
