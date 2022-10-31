"""
Assets related queries
"""

GQL_CREATE_UPLOAD_BUCKET_SIGNED_URLS = """
query($filePaths: [String!]) {
  urls: createUploadBucketSignedUrls(filePaths: $filePaths)
}
"""
