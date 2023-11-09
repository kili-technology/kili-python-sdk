"""GraphQL payload data mappers for label operations."""

import json
from typing import Dict

from kili.adapters.kili_api_gateway.asset.mappers import asset_where_mapper
from kili.adapters.kili_api_gateway.user.mappers import user_where_mapper
from kili.domain.label import LabelFilters

from .types import AppendLabelData, AppendToLabelsData, UpdateLabelData


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
        "project": {"id": filters.project_id},
        "reviewerIn": filters.reviewer_in,
        "search": filters.search,
        "typeIn": filters.type_in,
        "user": user_where_mapper(filters.user) if filters.user else None,
    }


def update_label_data_mapper(data: UpdateLabelData) -> Dict:
    """Map UpdateLabelData to GraphQL LabelData input."""
    return {
        "isSentBackToQueue": data.is_sent_back_to_queue,
        "jsonResponse": json.dumps(data.json_response) if data.json_response else None,
        "modelName": data.model_name,
        "secondsToLabel": data.seconds_to_label,
    }


def append_label_data_mapper(data: AppendLabelData) -> Dict:
    """Map AppendLabelData to GraphQL AppendLabelData input."""
    return {
        "authorID": data.author_id,
        "assetID": data.asset_id,
        "clientVersion": data.client_version,
        "jsonResponse": json.dumps(data.json_response),
        "secondsToLabel": data.seconds_to_label,
        "modelName": data.model_name,
    }


def append_to_labels_data_mapper(data: AppendToLabelsData) -> Dict:
    """Map AppendToLabelsData to GraphQL AppendToLabelsData input."""
    return {
        "authorID": data.author_id,
        "clientVersion": data.client_version,
        "jsonResponse": json.dumps(data.json_response),
        "labelType": data.label_type,
        "secondsToLabel": data.seconds_to_label,
        "skipped": data.skipped,
    }
