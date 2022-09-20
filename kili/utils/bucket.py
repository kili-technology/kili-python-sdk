"""Module for managing bucket's signed urls"""


from typing import Union
from urllib.parse import urlparse

import requests

from kili.authentication import KiliAuth
from kili.graphql.operations.asset.queries import GQL_CREATE_UPLOAD_BUCKET_SIGNED_URLS

AZURE_STRING = "blob.core.windows.net"
GCP_STRING = "storage.googleapis.com"
GCP_STRING_PUBLIC = "storage.cloud.google.com"


def request_signed_urls(auth: KiliAuth, project_id: str, size: int):
    """
    Get upload signed URLs
    Args:
        auth: Kili Auth
        project_id: the project Id
        size: the amount of upload signed URL to query
    """
    payload = {
        "projectID": project_id,
        "size": size,
    }
    urls_response = auth.client.execute(GQL_CREATE_UPLOAD_BUCKET_SIGNED_URLS, payload)
    return urls_response["data"]["urls"]


def upload_data_via_rest(url_with_id: str, data: Union[str, bytes], content_type: str):
    """upload data in buckets' signed URL via REST
    Args:
        signed_urls: Bucket signed URLs to upload local files to
        path_array: a list of file paths, json or text to upload
        content_type: mimetype of the data. It will be infered if not given
    """
    headers = {"Content-type": content_type}
    url_to_use_for_upload = url_with_id.split("&id=")[0]
    if "blob.core.windows.net" in url_to_use_for_upload:
        headers["x-ms-blob-type"] = "BlockBlob"

    response = requests.put(url_to_use_for_upload, data=data, headers=headers)
    response.raise_for_status()
    return url_with_id


AZURE_STRING = "blob.core.windows.net"
GCP_STRING = "storage.googleapis.com"
GCP_STRING_PUBLIC = "storage.cloud.google.com"


def clean_signed_url(url: str):
    if AZURE_STRING in url:
        return url.split("?")[0]
    if GCP_STRING in url:
        url_path = urlparse(url).path
        return f"https://{GCP_STRING_PUBLIC}{url_path}"
    return url
