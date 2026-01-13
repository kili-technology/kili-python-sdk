"""Formatters for assets retrieved from Kili API."""

import asyncio
import json
import os

import httpx

from kili.adapters.http_client import HttpClient
from kili.core.helpers import is_url
from kili.domain.types import ListOrTuple

# Batch size for parallel JSON response downloads (same as export service)
JSON_RESPONSE_BATCH_SIZE = 10


def load_json_from_link(link: str, http_client: HttpClient) -> dict:
    """Load json from link (synchronous fallback for non-batch operations)."""
    if link == "" or not is_url(link):
        return {}

    response = http_client.get(link, timeout=30)
    response.raise_for_status()
    return response.json()


async def _download_json_response(url: str) -> dict:
    """Download and parse JSON response from a URL using asyncio.

    Args:
        url: URL to download the JSON response from

    Returns:
        Parsed JSON response as a dictionary
    """
    try:
        verify_env = os.getenv("KILI_VERIFY")
        verify = verify_env.lower() in ("true", "1", "yes") if verify_env is not None else True

        async with httpx.AsyncClient(verify=verify) as client:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            return response.json()
    except (httpx.HTTPError, json.JSONDecodeError):
        # Return empty dict on error to ensure consistent response format
        return {}


async def _download_json_responses_async(url_to_label_mapping: list[tuple[str, dict]]) -> None:
    """Download JSON responses in parallel using asyncio.

    Args:
        url_to_label_mapping: List of tuples (url, label_dict) to download
    """
    # Process in batches to limit concurrent connections
    for i in range(0, len(url_to_label_mapping), JSON_RESPONSE_BATCH_SIZE):
        batch = url_to_label_mapping[i : i + JSON_RESPONSE_BATCH_SIZE]

        # Download all URLs in the batch in parallel using asyncio.gather
        download_tasks = [_download_json_response(url) for url, _ in batch]
        json_responses = await asyncio.gather(*download_tasks)

        # Assign the downloaded responses back to their labels and remove the URL
        for (_, label), json_response in zip(batch, json_responses, strict=False):
            label["jsonResponse"] = json_response
            if "jsonResponseUrl" in label:
                del label["jsonResponseUrl"]


def download_json_responses_parallel(url_to_label_mapping: list[tuple[str, dict]]) -> None:
    """Download JSON responses in parallel and assign to labels.

    Args:
        url_to_label_mapping: List of tuples (url, label_dict) to download
    """
    if not url_to_label_mapping:
        return

    # Run async downloads in a synchronous context
    asyncio.run(_download_json_responses_async(url_to_label_mapping))


def _parse_label_json_response(label: dict) -> None:
    """Parse jsonResponse string to dict for a single label.

    Args:
        label: Label dict to update in place
    """
    json_response_value = label.get("jsonResponse", "{}")
    try:
        label["jsonResponse"] = json.loads(json_response_value)
    except json.JSONDecodeError:
        label["jsonResponse"] = {}


def _process_label_json_response(label: dict, url_to_label_mapping: list[tuple[str, dict]]) -> None:
    """Process a single label's jsonResponse, either scheduling URL download or parsing.

    Args:
        label: Label dict to process
        url_to_label_mapping: List to append URL mapping if download needed
    """
    json_response_url = label.get("jsonResponseUrl")
    if json_response_url and is_url(json_response_url):
        url_to_label_mapping.append((json_response_url, label))
    else:
        _parse_label_json_response(label)


def load_asset_json_fields(asset: dict, fields: ListOrTuple[str], http_client: HttpClient) -> dict:
    """Load json fields of an asset."""
    if "jsonMetadata" in fields:
        try:
            asset["jsonMetadata"] = json.loads(asset.get("jsonMetadata", "{}"))
        except json.JSONDecodeError:
            asset["jsonMetadata"] = {}

    if "ocrMetadata" in fields and asset.get("ocrMetadata") is not None:
        asset["ocrMetadata"] = load_json_from_link(asset.get("ocrMetadata", ""), http_client)

    # Collect all URLs to download in parallel (similar to export service)
    url_to_label_mapping = []

    if "labels.jsonResponse" in fields:
        for label in asset.get("labels", []):
            _process_label_json_response(label, url_to_label_mapping)

    if "latestLabel.jsonResponse" in fields and asset.get("latestLabel") is not None:
        _process_label_json_response(asset["latestLabel"], url_to_label_mapping)

    if url_to_label_mapping:
        download_json_responses_parallel(url_to_label_mapping)

    return asset
