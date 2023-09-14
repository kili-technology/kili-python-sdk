"""GraphQL payload data mappers for project operations."""

from typing import Dict

from kili.domain.project import ProjectFilters

from .types import ProjectDataKiliAPIGatewayInput


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


def project_data_mapper(data: ProjectDataKiliAPIGatewayInput) -> Dict:
    """Build the GraphQL ProjectData variable to be sent in an operation."""
    return {
        "archived": data.archived,
        "author": data.author,
        "complianceTags": data.compliance_tags,
        "consensusMark": data.consensus_mark,
        "consensusTotCoverage": data.consensus_tot_coverage,
        "description": data.description,
        "canNavigateBetweenAssets": data.can_navigate_between_assets,
        "canSkipAsset": data.can_skip_asset,
        "honeypotMark": data.honeypot_mark,
        "inputType": data.input_type,
        "instructions": data.instructions,
        "jsonInterface": data.json_interface,
        "metadataTypes": data.metadata_types,
        "minConsensusSize": data.min_consensus_size,
        "numberOfAssets": data.number_of_assets,
        "rules": data.rules,
        "numberOfSkippedAssets": data.number_of_skipped_assets,
        "numberOfRemainingAssets": data.number_of_remaining_assets,
        "numberOfReviewedAssets": data.number_of_reviewed_assets,
        "reviewCoverage": data.review_coverage,
        "shouldRelaunchKpiComputation": data.should_relaunch_kpi_computation,
        "title": data.title,
        "useHoneyPot": data.use_honeypot,
    }
