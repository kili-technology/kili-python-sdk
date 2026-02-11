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
