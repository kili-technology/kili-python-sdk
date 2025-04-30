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
        "organizationId": filters.organization_id,
        "tagIds": filters.tag_ids,
        "deleted": filters.deleted,
    }
    if filters.archived is not None:
        ret["archived"] = filters.archived
    return ret


def project_data_mapper(data: ProjectDataKiliAPIGatewayInput) -> Dict:
    """Build the GraphQL ProjectData variable to be sent in an operation."""
    result = {
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
        "minConsensusSize": data.min_consensus_size,
        "rules": data.rules,
        "reviewCoverage": data.review_coverage,
        "shouldAutoAssign": data.should_auto_assign,
        "shouldRelaunchKpiComputation": data.should_relaunch_kpi_computation,
        "title": data.title,
        "useHoneyPot": data.use_honeypot,
    }

    if data.metadata_properties is not None:
        result["metadataProperties"] = data.metadata_properties
    elif data.metadata_types is not None:
        metadata_properties = {}
        for key, type_value in data.metadata_types.items():
            metadata_properties[key] = {
                "filterable": True,
                "type": type_value,
                "visibleByLabeler": True,
                "visibleByReviewer": True,
            }
        result["metadataProperties"] = metadata_properties

    return result
