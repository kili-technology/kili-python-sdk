"""
Assets related queries
"""

GQL_CREATE_UPLOAD_BUCKET_SIGNED_URLS = """
query($size: Int) {
  urls: createUploadBucketSignedUrls(size: $size)
}
"""
