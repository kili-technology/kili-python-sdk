"""GraphQL payload data mappers for project operations."""

from typing import Dict

from kili.domain.project import ProjectFilters


def project_where_mapper(filters: ProjectFilters) -> Dict:
    """Build the GraphQL ProjectWhere variable to be sent in an operation."""
    ret = {
        "id": filters.id,
        "searchQuery": filters.search_query,
        "shouldRelaunchKpiComputation": filters.should_relaunch_kpi_computation,
        "starred": filters.starred,
        "updatedAtGte": filters.updated_at_gte,
        "updatedAtLte": filters.updated_at_lte,
        "createdAtGte": filters.created_at_gte,
        "createdAtLte": filters.created_at_lte,
        "tagIds": filters.tag_ids,
    }
    if filters.archived is not None:
        ret["archived"] = filters.archived
    return ret
