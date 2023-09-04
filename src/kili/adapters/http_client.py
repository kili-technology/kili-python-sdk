"""HTTP client used to send requests to Kili."""
from typing import Union

import requests


class HttpClient:
    """HTTP client used to send requests to Kili.

    Will use the API key if the URL starts with the Kili endpoint.
    """

    def __init__(self, kili_endpoint: str, api_key: str, verify: Union[bool, str]) -> None:
        """Initialize the HTTP client."""
        self._kili_endpoint = kili_endpoint

        self._http_client = requests.Session()
        self._http_client_with_auth = requests.Session()
        self._http_client_with_auth.headers.update({"Authorization": f"X-API-Key: {api_key}"})

        self._http_client.verify = verify
        self._http_client_with_auth.verify = verify

    def get(self, url: str, **kwargs) -> requests.Response:
        """Send a GET request to the given URL."""
        if url.startswith(self._kili_endpoint):
            return self._http_client_with_auth.get(url, **kwargs)
        return self._http_client.get(url, **kwargs)

    def post(self, url: str, **kwargs) -> requests.Response:
        """Send a POST request to the given URL."""
        if url.startswith(self._kili_endpoint):
            return self._http_client_with_auth.post(url, **kwargs)
        return self._http_client.post(url, **kwargs)

    def head(self, url: str, **kwargs) -> requests.Response:
        """Send a HEAD request to the given URL."""
        if url.startswith(self._kili_endpoint):
            return self._http_client_with_auth.head(url, **kwargs)
        return self._http_client.head(url, **kwargs)

    def put(self, url: str, **kwargs) -> requests.Response:
        """Send a PUT request to the given URL."""
        if url.startswith(self._kili_endpoint):
            return self._http_client_with_auth.put(url, **kwargs)
        return self._http_client.put(url, **kwargs)
