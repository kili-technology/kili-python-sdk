"""Module for managing bucket's signed urls"""


from typing import Union
from urllib.parse import parse_qs, urlparse

import requests
from tenacity import retry
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_random

from kili.authentication import KiliAuth
from kili.graphql.operations.asset.queries import GQL_CREATE_UPLOAD_BUCKET_SIGNED_URLS

AZURE_STRING = "blob.core.windows.net"
GCP_STRING = "storage.googleapis.com"
GCP_STRING_PUBLIC = "storage.cloud.google.com"

MAX_NUMBER_SIGNED_URLS_TO_FETCH = 30


def request_signed_urls(auth: KiliAuth, project_id: str, size: int):
    """
    Get upload signed URLs
    Args:
        auth: Kili Auth
        project_id: the project Id
        size: the amount of upload signed URL to query
    """
    signed_urls = []
    while len(signed_urls) < size:
        nb_url_requested = min(MAX_NUMBER_SIGNED_URLS_TO_FETCH, size - len(signed_urls))
        payload = {
            "projectID": project_id,
            "size": nb_url_requested,
        }
        urls_response = auth.client.execute(GQL_CREATE_UPLOAD_BUCKET_SIGNED_URLS, payload)
        signed_urls.extend(urls_response["data"]["urls"])
    return signed_urls


@retry(stop=stop_after_attempt(3), wait=wait_random(min=1, max=2))
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


def clean_signed_url(url: str, endpoint: str):
    """
    return a cleaned sined url for frame upload
    """
    query = urlparse(url).query
    id_param = parse_qs(query)["id"][0]
    base_path = endpoint.replace("/graphql", "/files").replace("http://", "https://")
    return f"{base_path}?id={id_param}"
