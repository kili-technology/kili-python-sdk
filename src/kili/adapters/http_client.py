"""HTTP client."""

from typing import Union

import requests


class HttpClient:
    """HTTP client.

    Will use the API key if the URL starts with the Kili endpoint.
    """

    def __init__(self, kili_endpoint: str, api_key: str, verify: Union[bool, str]) -> None:
        """Initialize the HTTP client."""
        self._kili_endpoint = kili_endpoint.replace("/api/label/v2/graphql", "/api/label/v2")

        self._http_client = requests.Session()
        self._http_client_with_auth = requests.Session()

        self._http_client.verify = verify
        self._http_client_with_auth.verify = verify

        self._auth_headers = {"Authorization": f"X-API-Key: {api_key}"}
        self._http_client_with_auth.headers.update(self._auth_headers)

    def _send_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Send a request to the given URL."""
        if url.startswith(self._kili_endpoint):
            http_client = self._http_client_with_auth
            # if headers are provided, we need to update the headers with the api key
            if kwargs.get("headers") is not None and "Authorization" not in kwargs["headers"]:
                kwargs["headers"].update(self._auth_headers)
        else:
            http_client = self._http_client

        return http_client.request(method, url, **kwargs)

    def get(self, url: str, **kwargs) -> requests.Response:
        """Send a GET request to the given URL."""
        return self._send_request("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> requests.Response:
        """Send a POST request to the given URL."""
        return self._send_request("POST", url, **kwargs)

    def head(self, url: str, **kwargs) -> requests.Response:
        """Send a HEAD request to the given URL."""
        return self._send_request("HEAD", url, **kwargs)

    def put(self, url: str, **kwargs) -> requests.Response:
        """Send a PUT request to the given URL."""
        return self._send_request("PUT", url, **kwargs)

    def patch(self, url: str, **kwargs) -> requests.Response:
        """Send a PATCH request to the given URL."""
        return self._send_request("PATCH", url, **kwargs)

    def options(self, url: str, **kwargs) -> requests.Response:
        """Send a OPTIONS request to the given URL."""
        return self._send_request("OPTIONS", url, **kwargs)
