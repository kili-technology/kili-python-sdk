"""GraphQL payload data mappers for label operations."""

from typing import Dict

from kili.adapters.kili_api_gateway.asset.mappers import asset_where_mapper
from kili.adapters.kili_api_gateway.project.mappers import project_where_mapper
from kili.adapters.kili_api_gateway.user.mappers import user_where_mapper
from kili.domain.label import LabelFilters


def label_where_mapper(filters: LabelFilters) -> Dict[str, object]:
    """Map label filters to GraphQL LabelWhere."""
    return {
        "asset": asset_where_mapper(filters.asset) if filters.asset else None,
        "authorIn": filters.author_in,
        "consensusMarkGte": filters.consensus_mark_gte,
        "consensusMarkLte": filters.consensus_mark_lte,
        "createdAt": filters.created_at,
        "createdAtGte": filters.created_at_gte,
        "createdAtLte": filters.created_at_lte,
        "honeypotMarkGte": filters.honeypot_mark_gte,
        "honeypotMarkLte": filters.honeypot_mark_lte,
        "id": filters.id,
        "idIn": filters.id_in,
        "labelerIn": filters.labeler_in,
        "project": project_where_mapper(filters.project) if filters.project else None,
        "reviewerIn": filters.reviewer_in,
        "search": filters.search,
        "typeIn": filters.type_in,
        "user": user_where_mapper(filters.user) if filters.user else None,
    }
