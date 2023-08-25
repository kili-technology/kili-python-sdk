"""GraphQL Queries of Assets."""


from dataclasses import dataclass
from typing import List, Optional

from kili.domain.issue import IssueStatus, IssueType
from kili.gateways.kili_api_gateway.queries import AbstractQueryWhere


@dataclass
class AssetWhere(AbstractQueryWhere):
    """Tuple to be passed to the AssetQuery to restrict query."""

    # pylint: disable=too-many-instance-attributes
    project_id: str
    asset_id: Optional[str] = None
    asset_id_in: Optional[List[str]] = None
    asset_id_not_in: Optional[List[str]] = None
    consensus_mark_gte: Optional[float] = None
    consensus_mark_lte: Optional[float] = None
    external_id_strictly_in: Optional[List[str]] = None
    external_id_in: Optional[List[str]] = None
    honeypot_mark_gte: Optional[float] = None
    honeypot_mark_lte: Optional[float] = None
    label_author_in: Optional[List[str]] = None
    label_consensus_mark_gte: Optional[float] = None
    label_consensus_mark_lte: Optional[float] = None
    label_created_at: Optional[str] = None
    label_created_at_gte: Optional[str] = None
    label_created_at_lte: Optional[str] = None
    label_honeypot_mark_gte: Optional[float] = None
    label_honeypot_mark_lte: Optional[float] = None
    label_type_in: Optional[List[str]] = None
    label_reviewer_in: Optional[List[str]] = None
    metadata_where: Optional[dict] = None
    skipped: Optional[bool] = None
    status_in: Optional[List[str]] = None
    updated_at_gte: Optional[str] = None
    updated_at_lte: Optional[str] = None
    label_category_search: Optional[str] = None
    created_at_gte: Optional[str] = None
    created_at_lte: Optional[str] = None
    inference_mark_gte: Optional[float] = None
    inference_mark_lte: Optional[float] = None
    issue_type: Optional[IssueType] = None
    issue_status: Optional[IssueStatus] = None

    def get_graphql_where_value(self):
        """Build the GraphQL AssetWhere variable to be sent in an operation."""

        return {
            "id": self.asset_id,
            "project": {
                "id": self.project_id,
            },
            "externalIdStrictlyIn": self.external_id_strictly_in,
            "externalIdIn": self.external_id_in,
            "statusIn": self.status_in,
            "consensusMarkGte": self.consensus_mark_gte,
            "consensusMarkLte": self.consensus_mark_lte,
            "honeypotMarkGte": self.honeypot_mark_gte,
            "honeypotMarkLte": self.honeypot_mark_lte,
            "idIn": self.asset_id_in,
            "idNotIn": self.asset_id_not_in,
            "metadata": self.metadata_where,
            "label": {
                "typeIn": self.label_type_in,
                "authorIn": self.label_author_in,
                "consensusMarkGte": self.label_consensus_mark_gte,
                "consensusMarkLte": self.label_consensus_mark_lte,
                "createdAt": self.label_created_at,
                "createdAtGte": self.label_created_at_gte,
                "createdAtLte": self.label_created_at_lte,
                "honeypotMarkGte": self.label_honeypot_mark_gte,
                "honeypotMarkLte": self.label_honeypot_mark_lte,
                "search": self.label_category_search,
                "reviewerIn": self.label_reviewer_in,
            },
            "skipped": self.skipped,
            "updatedAtGte": self.updated_at_gte,
            "updatedAtLte": self.updated_at_lte,
            "createdAtGte": self.created_at_gte,
            "createdAtLte": self.created_at_lte,
            "inferenceMarkGte": self.inference_mark_gte,
            "inferenceMarkLte": self.inference_mark_lte,
            "issue": {
                "type": self.issue_type,
                "status": self.issue_status,
            },
        }
