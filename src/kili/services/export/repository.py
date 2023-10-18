"""Gets the."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, List

from kili.adapters.http_client import HttpClient

from .exceptions import DownloadError


class AbstractContentRepository(ABC):
    """Interface to the content repository."""

    def __init__(self, router_endpoint: str, http_client: HttpClient) -> None:
        self.router_endpoint = router_endpoint
        self.http_client = http_client
        assert router_endpoint, "The router endpoint string should not be empty"

    @abstractmethod
    def get_frames(self, content_url: str) -> List[str]:
        """Get asset content frames."""

    @abstractmethod
    def get_content_stream(self, content_url: str, block_size: int) -> Iterator[Any]:
        """Get asset content stream."""

    def get_content_frames_paths(self, asset: Dict) -> List[str]:
        """Get list of links to frames from the file located at asset[jsonContent].

        Returns an empty list if `content` in the asset exists.
        """
        content_frames = []

        if not asset["content"] and asset["jsonContent"]:
            content_frames = self.get_frames(asset["jsonContent"])

        return content_frames

    def is_serving(self, url: str) -> bool:
        """Return a boolean defining if the asset is served by Kili or not."""
        return url.startswith(self.router_endpoint)


class SDKContentRepository(AbstractContentRepository):
    """Handle content fetching from the server from the SDK."""

    def get_frames(self, content_url: str) -> List[str]:
        frames: List[str] = []
        json_content_resp = self.http_client.get(content_url, timeout=30)

        if json_content_resp.ok:
            frames = list(json_content_resp.json().values())
        return frames

    def get_content_stream(self, content_url: str, block_size: int) -> Iterator[Any]:
        response = self.http_client.get(content_url, stream=True, timeout=30)
        if not response.ok:
            raise DownloadError(f"Error while downloading image {content_url}")

        return response.iter_content(block_size)
