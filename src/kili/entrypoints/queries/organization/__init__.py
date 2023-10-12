"""Organization queries."""

from datetime import datetime
from typing import Dict, Optional

from typeguard import typechecked

from kili.core.graphql.graphql_client import GraphQLClient
from kili.core.graphql.operations.organization.queries import (
    OrganizationMetricsWhere,
    OrganizationQuery,
)
from kili.entrypoints.base import BaseOperationEntrypointMixin
from kili.utils.logcontext import for_all_methods, log_call


@for_all_methods(log_call, exclude=["__init__"])
class QueriesOrganization(BaseOperationEntrypointMixin):
    """Set of Organization queries."""

    graphql_client: GraphQLClient

    @typechecked
    def organization_metrics(
        self,
        organization_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict:
        """Get organization metrics.

        Args:
            organization_id: Identifier of the organization
            start_date: Start date of the metrics computation
            end_date: End date of the metrics computation

        Returns:
            A dictionary containing the metrics of the organization.
        """
        if start_date is None:
            start_date = datetime.now()
        if end_date is None:
            end_date = datetime.now()
        where = OrganizationMetricsWhere(
            organization_id=organization_id, start_date=start_date, end_date=end_date
        )
        return OrganizationQuery(self.graphql_client, self.http_client).metrics(where)
