"""
Assets related queries
"""

GQL_CREATE_UPLOAD_BUCKET_SIGNED_URLS = """
query($projectID: ID!, $size: Int) {
  urls: createUploadBucketSignedUrls(projectID: $projectID, size: $size)
}
"""
