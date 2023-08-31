"""Types for the Project-related Kili API gateway functions."""

from dataclasses import dataclass
from typing import Optional

from kili.adapters.kili_api_gateway.helpers.queries import AbstractQueryWhere


@dataclass
class ProjectWhere(AbstractQueryWhere):
    """Dataclass holding the parameters to query projects."""

    project_id: Optional[str] = None
    search_query: Optional[str] = None
    updated_at_gte: Optional[str] = None
    updated_at_lte: Optional[str] = None
    archived: Optional[bool] = None

    def build_gql_where(self):
        """Build the GraphQL Where payload sent in the resolver from the SDK ProjectWhere."""
        value = {
            "id": self.project_id,
            "searchQuery": self.search_query,
            "updatedAtGte": self.updated_at_gte,
            "updatedAtLte": self.updated_at_lte,
        }
        if self.archived is not None:
            value["archived"] = self.archived  # type: ignore
        return value
