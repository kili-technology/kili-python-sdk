"""
Gets the
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, List

import requests

from .exceptions import DownloadError


class AbstractContentRepository(ABC):
    """
    Interface to the content repository
    """

    def __init__(
        self, router_endpoint: str, router_headers: Dict[str, str], verify_ssl: bool
    ) -> None:
        self.router_endpoint = router_endpoint
        self.router_headers = router_headers
        self.verify_ssl = verify_ssl
        assert router_endpoint, "The router endpoint string should not be empty"

    @abstractmethod
    def get_frames(self, content_url: str) -> List[str]:
        """
        Get asset content frames.
        """

    @abstractmethod
    def get_content_stream(self, content_url: str, block_size: int) -> Iterator[Any]:
        """
        Get asset content stream.
        """

    def get_content_frames_paths(self, asset: Dict) -> List[str]:
        """
        Get list of links to frames from the file located at asset[jsonContent].
        Returns an empty list if `content` in the asset exists.
        """
        content_frames = []

        if not asset["content"] and asset["jsonContent"]:
            content_frames = self.get_frames(asset["jsonContent"])

        return content_frames

    def is_serving(self, url: str) -> bool:
        """
        Return a boolean defining if the asset is served by Kili or not
        """
        return url.startswith(self.router_endpoint)


class SDKContentRepository(AbstractContentRepository):
    """
    Handle content fetching from the server from the SDK
    """

    def get_frames(self, content_url: str) -> List[str]:
        frames: List[str] = []
        headers = None
        if content_url.startswith(self.router_endpoint):
            headers = self.router_headers
        json_content_resp = requests.get(
            content_url, headers=headers, verify=self.verify_ssl, timeout=30
        )

        if json_content_resp.ok:
            frames = list(json_content_resp.json().values())
        return frames

    def get_content_stream(self, content_url: str, block_size: int) -> Iterator[Any]:
        response = requests.get(
            content_url,
            stream=True,
            headers=None,
            verify=self.verify_ssl,
            timeout=30,
        )

        if not response.ok:
            response = requests.get(
                content_url,
                stream=True,
                headers=self.router_headers,  # pass the API key if first request failed
                verify=self.verify_ssl,
                timeout=30,
            )

            if not response.ok:
                raise DownloadError(f"Error while downloading image {content_url}")

        return response.iter_content(block_size)
