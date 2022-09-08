"""
Queries of asset queries
"""


def gql_assets(fragment):
    """
    Return the GraphQL assets query
    """
    return f"""
query($where: AssetWhere!, $first: PageSize!, $skip: Int!) {{
  data: assets(where: $where, skip: $skip, first: $first) {{
    {fragment}
  }}
}}
"""


GQL_ASSETS_COUNT = """
query($where: AssetWhere!) {
  data: countAssets(where: $where)
}
"""

GQL_CREATE_UPLOAD_BUCKET_SIGNED_URLS = """
query($projectID: ID!, $size: Int) {
  urls: createUploadBucketSignedUrls(projectID: $projectID, size: $size)
}
"""
