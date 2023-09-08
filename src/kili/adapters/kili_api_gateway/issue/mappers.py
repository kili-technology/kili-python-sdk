"""GraphQL payload data mappers for asset operations."""

from kili.domain.issue import IssueFilters


def issue_where_mapper(filters: IssueFilters):
    """Build the GraphQL IssueWhere variable to be sent in an operation."""
    return {
        "project": {"id": filters.project_id},
        "asset": {"id": filters.asset_id},
        "assetIn": filters.asset_id_in,
        "status": filters.status,
        "type": filters.issue_type,
    }
