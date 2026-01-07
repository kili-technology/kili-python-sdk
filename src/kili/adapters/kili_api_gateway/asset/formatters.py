"""Formatters for assets retrieved from Kili API."""

import json
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from kili.adapters.http_client import HttpClient
from kili.core.helpers import get_response_json, is_url, log_raise_for_status
from kili.domain.types import ListOrTuple

# Batch size for parallel JSON response downloads (same as export service)
JSON_RESPONSE_BATCH_SIZE = 10


def load_json_from_link(link: str, http_client: HttpClient) -> dict:
    """Load json from link."""
    if link == "" or not is_url(link):
        return {}

    response = http_client.get(link, timeout=30)
    log_raise_for_status(response)
    return get_response_json(response)


def download_json_responses_parallel(
    url_to_label_mapping: list[tuple[str, dict]], http_client: HttpClient
) -> None:
    """Download JSON responses in parallel and assign to labels.

    Args:
        url_to_label_mapping: List of tuples (url, label_dict) to download
        http_client: HTTP client to use for downloads
    """
    if not url_to_label_mapping:
        return

    # Process in batches to limit concurrent connections
    for i in range(0, len(url_to_label_mapping), JSON_RESPONSE_BATCH_SIZE):
        batch = url_to_label_mapping[i : i + JSON_RESPONSE_BATCH_SIZE]

        # Download all URLs in the batch in parallel
        with ThreadPoolExecutor(max_workers=JSON_RESPONSE_BATCH_SIZE) as executor:
            # Submit all download tasks
            future_to_label = {
                executor.submit(load_json_from_link, url, http_client): label
                for url, label in batch
            }

            # Collect results as they complete
            for future in as_completed(future_to_label):
                label = future_to_label[future]
                try:
                    json_response = future.result()
                    label["jsonResponse"] = json_response
                    if "jsonResponseUrl" in label:
                        del label["jsonResponseUrl"]
                except (requests.RequestException, json.JSONDecodeError, TimeoutError):
                    # Set empty dict to ensure consistent response format
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
