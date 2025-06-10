"""Module for managing bucket's signed urls."""

import itertools
import os
import sys
from typing import List, Union
from urllib.parse import parse_qs, urlparse

import cuid
from tenacity import retry
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_random

from kili.adapters.http_client import HttpClient

MAX_NUMBER_SIGNED_URLS_TO_FETCH = 30


def generate_unique_id() -> str:
    """Generate a unique id."""
    return cuid.cuid()


# pylint: disable=missing-type-doc
def request_signed_urls(kili, file_urls: List[str]) -> List[str]:
    """Get upload signed URLs.

    Args:
        kili: Kili
        file_urls: the paths in Kili bucket of the data you upload. It must respect
            the convention projects/:projectId/assets/xxx.
    """
    size = len(file_urls)
    file_batches = [
        file_urls[i : i + MAX_NUMBER_SIGNED_URLS_TO_FETCH]
        for i in range(0, size, MAX_NUMBER_SIGNED_URLS_TO_FETCH)
    ]

    request_function = kili.kili_api_gateway.create_upload_bucket_signed_urls

    return [*itertools.chain(*map(request_function, file_batches))]


@retry(stop=stop_after_attempt(3), wait=wait_random(min=1, max=2), reraise=True)
def upload_data_via_rest(
    url_with_id: str, data: Union[str, bytes], content_type: str, http_client: HttpClient
) -> str:
    """Upload data in buckets' signed URL via REST.

    Args:
        url_with_id: signed url with id
        data: data to upload
        content_type: mimetype of the data
        http_client: http client
    """
    if content_type == "text/plain":
        content_type += "; charset=utf-8"
    headers = {"Content-type": content_type}
    url_to_use_for_upload = url_with_id.split("&id=")[0]
    if "blob.core.windows.net" in url_to_use_for_upload:
        headers["x-ms-blob-type"] = "BlockBlob"
    try:
        # Do we not put a timeout here because it can take an arbitrary long time (ML-1395)
        response = http_client.put(url_to_use_for_upload, data=data, headers=headers)
    except OverflowError as error:
        python_version = (
            f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        )
        raise ValueError(
            f"Unable to upload file larger than 2GB with Python {python_version}. "
            f"This is caused by a known Python SSL limitation in versions ≤3.9 (Python bug #42853). "
            f"To fix this issue, please upgrade to Python 3.10 or later. "
            f"Alternatively, compress your file or split it into smaller chunks before uploading. "
            f"For more details, see: https://bugs.python.org/issue42853"
        ) from error
    response.raise_for_status()
    return url_with_id


def clean_signed_url(url: str, endpoint: str) -> str:
    """Return a cleaned signed url for frame upload."""
    query = urlparse(url).query
    id_param = parse_qs(query)["id"][0]
    # Check if Kili is using http or https
    kili_path = os.getenv(
        "KILI_API_ENDPOINT", "https://cloud.kili-technology.com/api/label/v2/graphql"
    )
    is_using_http = kili_path.startswith("http://")
    if is_using_http:
        base_path = endpoint.replace("https://", "http://")
    else:
        base_path = endpoint.replace("http://", "https://")

    base_path = endpoint.replace("/graphql", "/files")
    return f"{base_path}?id={id_param}"
