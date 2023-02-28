"""
GraphQL Queries of Assets
"""


from typing import List, Optional

from kili.graphql import BaseQueryWhere, GraphQLQuery
from kili.orm import Asset as AssetFormatType


class AssetWhere(BaseQueryWhere):
    """
    Tuple to be passed to the AssetQuery to restrict query
    """

    # pylint: disable=too-many-arguments,too-many-locals,too-many-instance-attributes

    def __init__(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_id_in: Optional[List[str]] = None,
        consensus_mark_gt: Optional[float] = None,
        consensus_mark_lt: Optional[float] = None,
        external_id_contains: Optional[List[str]] = None,
        honeypot_mark_gt: Optional[float] = None,
        honeypot_mark_lt: Optional[float] = None,
        label_author_in: Optional[List[str]] = None,
        label_consensus_mark_gt: Optional[float] = None,
        label_consensus_mark_lt: Optional[float] = None,
        label_created_at: Optional[str] = None,
        label_created_at_gt: Optional[str] = None,
        label_created_at_lt: Optional[str] = None,
        label_honeypot_mark_gt: Optional[float] = None,
        label_honeypot_mark_lt: Optional[float] = None,
        label_type_in: Optional[List[str]] = None,
        metadata_where: Optional[dict] = None,
        skipped: Optional[bool] = None,
        status_in: Optional[List[str]] = None,
        updated_at_gte: Optional[str] = None,
        updated_at_lte: Optional[str] = None,
        label_category_search: Optional[str] = None,
        created_at_gte: Optional[str] = None,
        created_at_lte: Optional[str] = None,
    ):
        self.project_id = project_id
        self.asset_id = asset_id
        self.asset_id_in = asset_id_in
        self.consensus_mark_gt = consensus_mark_gt
        self.consensus_mark_lt = consensus_mark_lt
        self.external_id_contains = external_id_contains
        self.honeypot_mark_gt = honeypot_mark_gt
        self.honeypot_mark_lt = honeypot_mark_lt
        self.label_author_in = label_author_in
        self.label_consensus_mark_gt = label_consensus_mark_gt
        self.label_consensus_mark_lt = label_consensus_mark_lt
        self.label_created_at = label_created_at
        self.label_created_at_gt = label_created_at_gt
        self.label_created_at_lt = label_created_at_lt
        self.label_honeypot_mark_gt = label_honeypot_mark_gt
        self.label_honeypot_mark_lt = label_honeypot_mark_lt
        self.label_type_in = label_type_in
        self.metadata_where = metadata_where
        self.skipped = skipped
        self.status_in = status_in
        self.updated_at_gte = updated_at_gte
        self.updated_at_lte = updated_at_lte
        self.label_category_search = label_category_search
        self.created_at_gte = created_at_gte
        self.created_at_lte = created_at_lte
        super().__init__()

    def graphql_where_builder(self):
        """Build the GraphQL Where payload sent in the resolver from the SDK AssetWhere"""
        return {
            "id": self.asset_id,
            "project": {
                "id": self.project_id,
            },
            "externalIdStrictlyIn": self.external_id_contains,
            "statusIn": self.status_in,
            "consensusMarkGte": self.consensus_mark_gt,
            "consensusMarkLte": self.consensus_mark_lt,
            "honeypotMarkGte": self.honeypot_mark_gt,
            "honeypotMarkLte": self.honeypot_mark_lt,
            "idIn": self.asset_id_in,
            "metadata": self.metadata_where,
            "label": {
                "typeIn": self.label_type_in,
                "authorIn": self.label_author_in,
                "consensusMarkGte": self.label_consensus_mark_gt,
                "consensusMarkLte": self.label_consensus_mark_lt,
                "createdAt": self.label_created_at,
                "createdAtGte": self.label_created_at_gt,
                "createdAtLte": self.label_created_at_lt,
                "honeypotMarkGte": self.label_honeypot_mark_gt,
                "honeypotMarkLte": self.label_honeypot_mark_lt,
                "search": self.label_category_search,
            },
            "skipped": self.skipped,
            "updatedAtGte": self.updated_at_gte,
            "updatedAtLte": self.updated_at_lte,
            "createdAtGte": self.created_at_gte,
            "createdAtLte": self.created_at_lte,
        }


class AssetQuery(GraphQLQuery):
    """Asset query."""

    FORMAT_TYPE = AssetFormatType

    @staticmethod
    def query(fragment):
        """
        Return the GraphQL assets query
        """
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
