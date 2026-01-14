"""Formatters for assets retrieved from Kili API."""

import asyncio
import json

import requests

from kili.adapters.http_client import HttpClient
from kili.adapters.kili_api_gateway.helpers.http_json import load_json_from_link
from kili.core.helpers import is_url
from kili.domain.types import ListOrTuple

# Batch size for parallel JSON response downloads (same as export service)
JSON_RESPONSE_BATCH_SIZE = 10


async def _download_json_response(url: str, http_client: HttpClient) -> dict:
    """Download and parse JSON response from a URL using asyncio.

    Args:
        url: URL to download the JSON response from
        http_client: HttpClient instance with SSL verification already configured

    Returns:
        Parsed JSON response as a dictionary
    """
    try:
        # Run synchronous requests call in a thread
        response = await asyncio.to_thread(http_client.get, url, timeout=30)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, json.JSONDecodeError):
        # Return empty dict on error to ensure consistent response format
        return {}


async def _download_json_responses_async(
    url_to_label_mapping: list[tuple[str, dict]], http_client: HttpClient
) -> None:
    """Download JSON responses in parallel using asyncio.

    Args:
        url_to_label_mapping: List of tuples (url, label_dict) to download
        http_client: HttpClient instance with SSL verification already configured
    """
    # Process in batches to limit concurrent connections
    for i in range(0, len(url_to_label_mapping), JSON_RESPONSE_BATCH_SIZE):
        batch = url_to_label_mapping[i : i + JSON_RESPONSE_BATCH_SIZE]

        # Download all URLs in the batch in parallel using asyncio.gather
        download_tasks = [_download_json_response(url, http_client) for url, _ in batch]
        json_responses = await asyncio.gather(*download_tasks)

        # Assign the downloaded responses back to their labels and remove the URL
        for (_, label), json_response in zip(batch, json_responses, strict=False):
            label["jsonResponse"] = json_response
            if "jsonResponseUrl" in label:
                del label["jsonResponseUrl"]


def download_json_responses_parallel(
    url_to_label_mapping: list[tuple[str, dict]], http_client: HttpClient
) -> None:
    """Download JSON responses in parallel and assign to labels.

    Args:
        url_to_label_mapping: List of tuples (url, label_dict) to download
        http_client: HttpClient instance with SSL verification already configured
    """
    if not url_to_label_mapping:
        return

    # Check if we're already in an event loop (e.g., Jupyter notebook, async web framework)
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        # No running loop, safe to use asyncio.run() for parallel downloads
        asyncio.run(_download_json_responses_async(url_to_label_mapping, http_client))
    else:
        # Already in a loop - fall back to sequential downloads to avoid RuntimeError
        # This happens in Jupyter notebooks, FastAPI, and other async contexts
        for url, label in url_to_label_mapping:
            try:
                response = http_client.get(url, timeout=30)
                response.raise_for_status()
                label["jsonResponse"] = response.json()
            except (requests.RequestException, json.JSONDecodeError):
                label["jsonResponse"] = {}

            if "jsonResponseUrl" in label:
                del label["jsonResponseUrl"]


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
        download_json_responses_parallel(url_to_label_mapping, http_client)

    return asset
