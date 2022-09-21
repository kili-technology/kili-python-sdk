"""Module for managing bucket's signed urls"""

from typing import List

import requests

from kili.authentication import KiliAuth
from kili.graphql.operations.asset.queries import GQL_CREATE_UPLOAD_BUCKET_SIGNED_URLS


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


def upload_data_via_rest(
    signed_urls: List[str], data_array: List[str], content_type_array: List[str]
):
    """upload data in buckets' signed URL via REST
    Args:
        signed_urls: Bucket signed URLs to upload local files to
        path_array: a list of file paths, json or text to upload
        content_type: mimetype of the data. It will be infered if not given
    """
    responses = []
    for index, data in enumerate(data_array):
        content_type = content_type_array[index]
        headers = {"Content-type": content_type}
        url_with_id = signed_urls[index]
        url_to_use_for_upload = url_with_id.split("&id=")[0]
        if "blob.core.windows.net" in url_to_use_for_upload:
            headers["x-ms-blob-type"] = "BlockBlob"

        response = requests.put(url_to_use_for_upload, data=data, headers=headers)
        if response.status_code >= 300:
            responses.append("")
            continue
        responses.append(url_with_id)
    return responses
