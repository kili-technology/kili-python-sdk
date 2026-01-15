"""HTTP JSON helpers for downloading JSON data from URLs."""

from kili.adapters.http_client import HttpClient
from kili.core.helpers import is_url


def load_json_from_link(link: str, http_client: HttpClient) -> dict:
    """Load json from link.

    Args:
        link: URL to download JSON from
        http_client: HttpClient instance with SSL verification already configured

    Returns:
        Parsed JSON response as a dictionary, or empty dict if link is invalid
    """
    if link == "" or not is_url(link):
        return {}

    response = http_client.get(link, timeout=30)
    response.raise_for_status()
    return response.json()
