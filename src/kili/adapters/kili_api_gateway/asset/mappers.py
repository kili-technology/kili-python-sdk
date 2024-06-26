"""GraphQL payload data mappers for asset operations."""

import warnings

from kili.domain.asset import AssetFilters

MAX_PARTIAL_EXTERNAL_IDS_FILTER = 10


def asset_where_mapper(filters: AssetFilters):
    """Build the GraphQL AssetWhere variable to be sent in an operation."""
    if (
        filters.external_id_in is not None
        and len(filters.external_id_in) > MAX_PARTIAL_EXTERNAL_IDS_FILTER
    ):
        warnings.warn(
            f"Requesting more than {MAX_PARTIAL_EXTERNAL_IDS_FILTER} partial external IDs"
            "in a single query is deprecated. You can use the `external_id_strictly_in`"
            f"field to filter by more than {MAX_PARTIAL_EXTERNAL_IDS_FILTER} external IDs. "
            "This limit will be enforced in next versions.",
            stacklevel=5,
        )
    return {
        "id": filters.asset_id,
        "project": {
            "id": filters.project_id,
        },
        "externalIdStrictlyIn": filters.external_id_strictly_in,
        "externalIdIn": filters.external_id_in,
        "statusIn": filters.status_in,
        "consensusMarkGte": filters.consensus_mark_gte,
        "consensusMarkLte": filters.consensus_mark_lte,
        "honeypotMarkGte": filters.honeypot_mark_gte,
        "honeypotMarkLte": filters.honeypot_mark_lte,
        "idIn": filters.asset_id_in,
        "idNotIn": filters.asset_id_not_in,
        "metadata": filters.metadata_where,
        "assigneeIn": filters.assignee_in,
        "assigneeNotIn": filters.assignee_not_in,
        "label": {
            "typeIn": filters.label_type_in,
            "authorIn": filters.label_author_in,
            "consensusMarkGte": filters.label_consensus_mark_gte,
            "consensusMarkLte": filters.label_consensus_mark_lte,
            "createdAt": filters.label_created_at,
            "createdAtGte": filters.label_created_at_gte,
            "createdAtLte": filters.label_created_at_lte,
            "honeypotMarkGte": filters.label_honeypot_mark_gte,
            "honeypotMarkLte": filters.label_honeypot_mark_lte,
            "search": filters.label_category_search,
            "labelerIn": filters.label_labeler_in,
            "labelerNotIn": filters.label_labeler_not_in,
            "reviewerIn": filters.label_reviewer_in,
            "reviewerNotIn": filters.label_reviewer_not_in,
        },
        "skipped": filters.skipped,
        "updatedAtGte": filters.updated_at_gte,
        "updatedAtLte": filters.updated_at_lte,
        "createdAtGte": filters.created_at_gte,
        "createdAtLte": filters.created_at_lte,
        "inferenceMarkGte": filters.inference_mark_gte,
        "inferenceMarkLte": filters.inference_mark_lte,
        "issue": {
            "type": filters.issue_type,
            "status": filters.issue_status,
        },
    }
