"""GraphQL Asset operations."""


def get_assets_query(fragment: str) -> str:
    """Return the GraphQL assets query."""
    return f"""
        query assets($where: AssetWhere!, $first: PageSize!, $skip: Int!) {{
            data: assets(where: $where, skip: $skip, first: $first) {{
                {fragment}
            }}
        }}
        """


GQL_COUNT_ASSETS = """
query countAssets($where: AssetWhere!) {
    data: countAssets(where: $where)
}
"""

GQL_LIST_ASSETS_METADATA_KEYS = """
query listAssetsMetadataKeys($where: AssetWhere!) {
    data: listAssetsMetadataKeys(where: $where)
}
"""

GQL_COUNT_ASSETS_BY_METADATA_VALUE = """
query countAssetsByMetadataValue($where: AssetWhere!, $metadataKey: String!) {
    data: countAssetsByMetadataValue(where: $where, metadataKey: $metadataKey) {
        values {
            value
            count
        }
        missingCount
    }
}
"""

GQL_CREATE_UPLOAD_BUCKET_SIGNED_URLS = """
query($filePaths: [String!]) {
  urls: createUploadBucketSignedUrls(filePaths: $filePaths)
}
"""


GQL_FILTER_EXISTING_ASSETS = """
query FilterExistingAssets($projectID: ID!, $externalIDs: [String!]!) {
  external_ids: filterExistingAssets(projectID: $projectID, externalIDs: $externalIDs)
}
"""

GQL_COUNT_ASSET_ANNOTATIONS = """
query countAssetAnnotations($where: AssetWhere!) {
    data: countAssetAnnotations(where: $where)
}
"""
