"""GraphQL payload data mappers for asset operations."""

from typing import Any

from kili.domain.issue import IssueFilters


def issue_where_mapper(filters: IssueFilters) -> dict[str, Any]:
    """Build the GraphQL IssueWhere variable to be sent in an operation."""
    return {
        "project": {"id": filters.project_id},
        "asset": {"id": filters.asset_id},
        "assetIn": filters.asset_id_in,
        "status": filters.status,
        "type": filters.issue_type,
    }
