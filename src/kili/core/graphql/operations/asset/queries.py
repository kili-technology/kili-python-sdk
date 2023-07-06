"""GraphQL Queries of Assets."""


from typing import List, Literal, Optional

from kili.core.graphql import BaseQueryWhere, GraphQLQuery
from kili.orm import Asset as AssetFormatType


class AssetWhere(BaseQueryWhere):
    """Tuple to be passed to the AssetQuery to restrict query."""

    # pylint: disable=too-many-arguments,too-many-locals,too-many-instance-attributes

    def __init__(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_id_in: Optional[List[str]] = None,
        asset_id_not_in: Optional[List[str]] = None,
        consensus_mark_gte: Optional[float] = None,
        consensus_mark_lte: Optional[float] = None,
        external_id_strictly_in: Optional[List[str]] = None,
        external_id_in: Optional[List[str]] = None,
        honeypot_mark_gte: Optional[float] = None,
        honeypot_mark_lte: Optional[float] = None,
        label_author_in: Optional[List[str]] = None,
        label_consensus_mark_gte: Optional[float] = None,
        label_consensus_mark_lte: Optional[float] = None,
        label_created_at: Optional[str] = None,
        label_created_at_gte: Optional[str] = None,
        label_created_at_lte: Optional[str] = None,
        label_honeypot_mark_gte: Optional[float] = None,
        label_honeypot_mark_lte: Optional[float] = None,
        label_type_in: Optional[List[str]] = None,
        label_reviewer_in: Optional[List[str]] = None,
        metadata_where: Optional[dict] = None,
        skipped: Optional[bool] = None,
        status_in: Optional[List[str]] = None,
        updated_at_gte: Optional[str] = None,
        updated_at_lte: Optional[str] = None,
        label_category_search: Optional[str] = None,
        created_at_gte: Optional[str] = None,
        created_at_lte: Optional[str] = None,
        inference_mark_gte: Optional[float] = None,
        inference_mark_lte: Optional[float] = None,
        issue_type: Optional[Literal["QUESTION", "ISSUE"]] = None,
        issue_status: Optional[Literal["OPEN", "SOLVED"]] = None,
    ) -> None:
        self.project_id = project_id
        self.asset_id = asset_id
        self.asset_id_in = asset_id_in
        self.asset_id_not_in = asset_id_not_in
        self.consensus_mark_gte = consensus_mark_gte
        self.consensus_mark_lte = consensus_mark_lte
        self.external_id_strictly_in = external_id_strictly_in
        self.external_id_in = external_id_in
        self.honeypot_mark_gte = honeypot_mark_gte
        self.honeypot_mark_lte = honeypot_mark_lte
        self.label_author_in = label_author_in
        self.label_consensus_mark_gte = label_consensus_mark_gte
        self.label_consensus_mark_lte = label_consensus_mark_lte
        self.label_created_at = label_created_at
        self.label_created_at_gte = label_created_at_gte
        self.label_created_at_lte = label_created_at_lte
        self.label_honeypot_mark_gte = label_honeypot_mark_gte
        self.label_honeypot_mark_lte = label_honeypot_mark_lte
        self.label_type_in = label_type_in
        self.label_reviewer_in = label_reviewer_in
        self.metadata_where = metadata_where
        self.skipped = skipped
        self.status_in = status_in
        self.updated_at_gte = updated_at_gte
        self.updated_at_lte = updated_at_lte
        self.label_category_search = label_category_search
        self.created_at_gte = created_at_gte
        self.created_at_lte = created_at_lte
        self.inference_mark_gte = inference_mark_gte
        self.inference_mark_lte = inference_mark_lte
        self.issue_type = issue_type
        self.issue_status = issue_status
        super().__init__()

    def graphql_where_builder(self):
        """Build the GraphQL Where payload sent in the resolver from the SDK AssetWhere."""
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


class AssetQuery(GraphQLQuery):
    """Asset query."""

    FORMAT_TYPE = AssetFormatType

    @staticmethod
    def query(fragment):
        """Return the GraphQL assets query."""
        return f"""
        query assets($where: AssetWhere!, $first: PageSize!, $skip: Int!) {{
            data: assets(where: $where, skip: $skip, first: $first) {{
                {fragment}
            }}
        }}
        """

    COUNT_QUERY = """
    query countAssets($where: AssetWhere!) {
        data: countAssets(where: $where)
    }
    """


GQL_CREATE_UPLOAD_BUCKET_SIGNED_URLS = """
query($filePaths: [String!]) {
  urls: createUploadBucketSignedUrls(filePaths: $filePaths)
}
"""
