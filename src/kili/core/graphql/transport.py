"""HTTP transport for the GraphQL client: request compression and size-aware timeouts."""

import gzip
import time
from dataclasses import dataclass
from typing import Any, Optional, Union

from gql.transport.requests import RequestsHTTPTransport
from requests import PreparedRequest, Response
from requests.adapters import HTTPAdapter

# Below 1 MB a body uploads in a few seconds even on a slow link, so compressing it gains little.
# Above, large JSON payloads (metadata, label json responses) compress several times over, which
# saves most of their upload time.
COMPRESSION_THRESHOLD_BYTES = 1_000_000
# zlib's default: most of the size gain of the higher levels, for a fraction of their CPU time.
COMPRESSION_LEVEL = 6
# Slowest upload a request is given time for: 100 kB/s, about 0.8 Mbit/s, a congested or mobile
# uplink. A body of 20 MB on the wire, say, gets 200 s to be sent.
MIN_UPLOAD_BYTES_PER_SECOND = 100_000


@dataclass(frozen=True)
class Exchange:
    """What one HTTP request cost, for the batch and page budgets."""

    payload_bytes: int  # request body, uncompressed
    response_bytes: int  # response body, decompressed
    seconds: float  # from sending the request to having read the whole response, or failed
    download_seconds: float  # reading the response body, once its headers arrived
    succeeded: bool  # answered with a 2xx


def scale_timeout(timeout: Any, body_bytes: int) -> Any:
    """Split a timeout into (connect, read), both with room for the body to be uploaded.

    urllib3 sends the body under the connect timeout, then waits for the answer under the read
    timeout. On a direct link the upload happens under the first, which never gets less than the
    caller's timeout. Behind a proxy that accepts the body at once and forwards it slowly, it
    happens under the second, before the server even starts: the caller's timeout is kept for
    the server, on top of the upload.
    """
    if isinstance(timeout, (int, float)):
        connect, read = timeout, timeout
    elif isinstance(timeout, tuple):
        connect, read = timeout
    else:
        return timeout  # None (wait forever) or a urllib3 Timeout set by the caller
    upload_seconds = body_bytes / MIN_UPLOAD_BYTES_PER_SECOND
    if connect is not None:
        connect = max(connect, upload_seconds)
    if read is not None:
        read += upload_seconds
    return connect, read


class KiliHTTPAdapter(HTTPAdapter):
    """Compresses large bodies, scales the timeouts to the body, and measures each exchange.

    The measurement is left in last_exchange for the GraphQL client, which knows whether the
    request was a query or a mutation. Requests go through one at a time (the client's execute
    lock), so last_exchange belongs to the request that just ended.
    """

    def __init__(self, compress_requests: bool = True, **kwargs: Any) -> None:
        # max_retries keeps requests' default of no retry: GraphQLClient decides what to retry
        super().__init__(**kwargs)
        self.compress_requests = compress_requests
        self.last_exchange: Optional[Exchange] = None

    def send(  # pylint: disable=too-many-arguments
        self,
        request: PreparedRequest,
        stream: bool = False,
        timeout: Any = None,
        verify: Union[bool, str] = True,
        cert: Any = None,
        proxies: Any = None,  # typed differently by requests' own hints and by its stubs
    ) -> Response:
        """Send the request and, unless it is streamed, read the response."""
        self.last_exchange = None
        payload_bytes = self._compress(request, self.compress_requests)
        wire_bytes = len(request.body) if isinstance(request.body, (bytes, str)) else 0
        start = time.perf_counter()  # monotonic() ticks every ~15 ms on Windows
        try:
            response = super().send(
                request,
                stream=stream,
                timeout=scale_timeout(timeout, wire_bytes),
                verify=verify,
                cert=cert,
                proxies=proxies,
            )
            headers_received = time.perf_counter()
            # requests would read the body right after anyway: reading it here times it too
            response_bytes = 0 if stream else len(response.content or b"")
        except Exception:
            self.last_exchange = Exchange(payload_bytes, 0, time.perf_counter() - start, 0.0, False)
            raise
        end = time.perf_counter()
        self.last_exchange = Exchange(
            payload_bytes, response_bytes, end - start, end - headers_received, response.ok
        )
        return response

    @staticmethod
    def _compress(request: PreparedRequest, enabled: bool = True) -> int:
        """Gzip the body in place when it is large, and return its uncompressed size."""
        body = request.body
        if body is None:
            # a 301/302 redirect turns the POST into a GET without a body
            if request.headers.get("Content-Encoding") == "gzip":
                del request.headers["Content-Encoding"]
            return 0
        if not isinstance(body, (bytes, str)):
            return 0  # multipart uploads are streamed, their size is unknown here
        raw = body.encode("utf-8") if isinstance(body, str) else body
        if (
            not enabled
            or len(raw) < COMPRESSION_THRESHOLD_BYTES
            or "Content-Encoding" in request.headers
        ):
            return len(raw)
        compressed = gzip.compress(raw, compresslevel=COMPRESSION_LEVEL)
        request.body = compressed
        request.headers["Content-Encoding"] = "gzip"
        request.headers["Content-Length"] = str(len(compressed))
        return len(raw)


class KiliRequestsHTTPTransport(RequestsHTTPTransport):
    """The requests transport of gql, with the Kili adapter mounted on each session."""

    def __init__(self, *args: Any, compress_requests: bool = True, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.adapter = KiliHTTPAdapter(compress_requests=compress_requests)

    def connect(self) -> None:
        """Open a session, which gql does for every operation, and mount the adapter on it."""
        super().connect()
        assert self.session is not None
        for prefix in ("http://", "https://"):
            self.session.mount(prefix, self.adapter)
