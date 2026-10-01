"""The GraphQL client against a local HTTP server, through the real transport, requests and urllib3."""

import base64
import gzip
import http.server
import json
import os
import socketserver
import threading
import time
from collections.abc import Callable, Iterator
from typing import Optional

import pytest
import pytest_mock

from kili.adapters.http_client import HttpClient
from kili.core.graphql.graphql_client import GraphQLClient, GraphQLClientName
from kili.exceptions import MutationOutcomeUnknownError

MUTATION = "mutation { appendManyAssets(data: {}) { id } }"
ENVOY_REFUSED = (
    b"upstream connect error or disconnect/reset before headers. reset reason: remote connection"
    b" failure, transport failure reason: delayed connect error: Connection refused"
)
ENVOY_RESET_AFTER_FORWARD = (
    b"upstream connect error or disconnect/reset before headers. reset reason: connection"
    b" termination"
)


class Backend:
    """Records the requests it receives; answers each with the next scripted reply."""

    def __init__(self) -> None:
        self.bodies: list[bytes] = []
        self.encodings: list[Optional[str]] = []
        self.replies: list[Callable[[http.server.BaseHTTPRequestHandler], None]] = []
        self.read_bytes_per_second: Optional[int] = None  # None: read the body at once

    def handle(self, handler: http.server.BaseHTTPRequestHandler) -> None:
        length = int(handler.headers["Content-Length"])
        self.bodies.append(self._read(handler, length))
        self.encodings.append(handler.headers.get("Content-Encoding"))
        reply = self.replies.pop(0) if self.replies else ok
        reply(handler)

    def _read(self, handler: http.server.BaseHTTPRequestHandler, length: int) -> bytes:
        if self.read_bytes_per_second is None:
            return handler.rfile.read(length)
        body = b""
        while len(body) < length:
            body += handler.rfile.read(min(65536, length - len(body)))
            time.sleep(65536 / self.read_bytes_per_second)
        return body


def ok(handler: http.server.BaseHTTPRequestHandler) -> None:
    body = json.dumps({"data": {"appendManyAssets": [{"id": "asset"}]}}).encode()
    handler.send_response(200)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def slow(handler: http.server.BaseHTTPRequestHandler) -> None:
    time.sleep(1.5)  # longer than the client's read timeout: the mutation outcome is unknown
    ok(handler)


def envoy_503(body: bytes) -> Callable[[http.server.BaseHTTPRequestHandler], None]:
    def reply(handler: http.server.BaseHTTPRequestHandler) -> None:
        handler.send_response(503)
        handler.send_header("Content-Length", str(len(body)))
        handler.end_headers()
        handler.wfile.write(body)

    return reply


@pytest.fixture()
def backend() -> Iterator[tuple[Backend, str]]:
    state = Backend()

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            state.handle(self)

        def log_message(self, format, *args):  # pylint: disable=redefined-builtin
            pass

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield state, f"http://127.0.0.1:{server.server_address[1]}/graphql"
    server.shutdown()


@pytest.fixture()
def client_for(mocker: pytest_mock.MockerFixture) -> Callable[..., GraphQLClient]:
    mocker.patch.dict("os.environ", {"KILI_SDK_SKIP_CHECKS": "true"})  # no schema introspection
    mocker.patch("kili.core.graphql.graphql_client._backoff", return_value=0)

    def build(endpoint: str, disable_request_compression: bool = False) -> GraphQLClient:
        return GraphQLClient(
            endpoint=endpoint,
            api_key="key",
            client_name=GraphQLClientName.SDK,
            http_client=HttpClient(kili_endpoint=endpoint, api_key="key", verify=True),
            enable_schema_caching=False,
            disable_request_compression=disable_request_compression,
        )

    return build


def test_a_mutation_that_times_out_reaches_the_server_once(backend, client_for):
    state, endpoint = backend
    state.replies = [slow]

    with pytest.raises(MutationOutcomeUnknownError):
        client_for(endpoint).execute(MUTATION, timeout=0.5)

    time.sleep(1)  # time for a resent copy to arrive, if one had been sent
    assert len(state.bodies) == 1


def test_a_mutation_envoy_could_not_forward_is_resent(backend, client_for):
    state, endpoint = backend
    state.replies = [envoy_503(ENVOY_REFUSED)]

    result = client_for(endpoint).execute(MUTATION)

    assert result == {"appendManyAssets": [{"id": "asset"}]}
    assert len(state.bodies) == 2


def test_a_mutation_reset_after_envoy_forwarded_it_is_not_resent(backend, client_for):
    state, endpoint = backend
    state.replies = [envoy_503(ENVOY_RESET_AFTER_FORWARD)]

    with pytest.raises(MutationOutcomeUnknownError):
        client_for(endpoint).execute(MUTATION)

    assert len(state.bodies) == 1


def test_a_mutation_that_drops_after_going_through_a_proxy_is_not_resent(client_for, mocker):
    received = []

    class Proxy(socketserver.BaseRequestHandler):
        """Reads the whole request, then closes the connection without answering."""

        def handle(self):
            data = b""
            while b"\r\n\r\n" not in data:
                data += self.request.recv(65536)
            head, _, body = data.partition(b"\r\n\r\n")
            length = next(
                int(line.split(b":")[1])
                for line in head.split(b"\r\n")
                if line.lower().startswith(b"content-length")
            )
            while len(body) < length:
                body += self.request.recv(65536)
            received.append(body)
            self.request.close()

    proxy = socketserver.ThreadingTCPServer(("127.0.0.1", 0), Proxy)
    threading.Thread(target=proxy.serve_forever, daemon=True).start()
    address = f"http://127.0.0.1:{proxy.server_address[1]}"
    # requests reads both cases, the lowercase first: neither may bypass the proxy
    mocker.patch.dict("os.environ", {"HTTP_PROXY": address, "http_proxy": address})
    for bypass in ("NO_PROXY", "no_proxy"):
        mocker.patch.dict("os.environ", {bypass: ""})
    try:
        with pytest.raises(MutationOutcomeUnknownError):
            client_for("http://kili.invalid/graphql").execute(MUTATION)
        time.sleep(1)  # time for a resent copy to arrive, if one had been sent
    finally:
        proxy.shutdown()

    assert len(received) == 1


def test_a_large_request_is_gzipped(backend, client_for):
    state, endpoint = backend
    metadata = "x" * 2_000_000

    client_for(endpoint).execute(
        "mutation($m: String) { appendManyAssets(data: {m: $m}) { id } }", {"m": metadata}
    )

    assert state.encodings == ["gzip"]
    assert json.loads(gzip.decompress(state.bodies[0]))["variables"] == {"m": metadata}


def test_a_slow_upload_is_given_the_time_to_arrive(backend, client_for):
    state, endpoint = backend
    state.read_bytes_per_second = 2_000_000  # 4 MB: about 2 s, well over the 0.5 s timeout
    metadata = base64.b64encode(os.urandom(3_000_000)).decode()  # does not compress

    client_for(endpoint, disable_request_compression=True).execute(
        "mutation($m: String) { appendManyAssets(data: {m: $m}) { id } }",
        {"m": metadata},
        timeout=0.5,
    )

    assert len(state.bodies) == 1
    assert json.loads(state.bodies[0])["variables"] == {"m": metadata}


def test_a_client_without_compression_sends_large_requests_as_is(backend, client_for):
    state, endpoint = backend
    metadata = "x" * 2_000_000

    client_for(endpoint, disable_request_compression=True).execute(
        "mutation($m: String) { appendManyAssets(data: {m: $m}) { id } }", {"m": metadata}
    )

    assert state.encodings == [None]
    assert json.loads(state.bodies[0])["variables"] == {"m": metadata}


LARGE = "x" * 200_000  # above the size at which a request tells something about throughput


def test_a_large_mutation_feeds_the_batch_budget(backend, client_for, mocker):
    _, endpoint = backend
    sizer = mocker.patch("kili.core.graphql.graphql_client.mutation_batch_sizer")

    client_for(endpoint).execute(
        "mutation($m: String) { appendManyAssets(data: {m: $m}) { id } }", {"m": LARGE}
    )

    sizer.record_success.assert_called_once()
    payload_bytes, seconds = sizer.record_success.call_args.args
    assert payload_bytes > len(LARGE)
    assert seconds > 0


def test_a_query_feeds_the_page_budget_not_the_batch_budget(backend, client_for, mocker):
    _, endpoint = backend
    batches = mocker.patch("kili.core.graphql.graphql_client.mutation_batch_sizer")
    pages = mocker.patch("kili.core.graphql.graphql_client.query_page_sizer")
    client = client_for(endpoint)

    client.execute("query($m: String) { assets(where: {m: $m}) { id } }", {"m": LARGE})

    batches.record_success.assert_not_called()
    batches.record_failure.assert_not_called()
    pages.sizer.record_success.assert_called_once()
    response_bytes, _ = pages.sizer.record_success.call_args.args
    assert response_bytes == client.last_response_bytes > 0


def test_a_large_mutation_that_times_out_shrinks_the_batch_budget(backend, client_for, mocker):
    state, endpoint = backend
    state.replies = [slow]
    sizer = mocker.patch("kili.core.graphql.graphql_client.mutation_batch_sizer")
    # keep the read timeout at 0.5 s: by default a 200 kB body is given 2 s to arrive
    mocker.patch("kili.core.graphql.transport.MIN_UPLOAD_BYTES_PER_SECOND", 10**9)

    with pytest.raises(MutationOutcomeUnknownError):
        client_for(endpoint).execute(
            "mutation($m: String) { appendManyAssets(data: {m: $m}) { id } }",
            {"m": LARGE},
            timeout=0.5,
        )

    sizer.record_failure.assert_called_once()
    assert sizer.record_failure.call_args.args[0] > len(LARGE)


def test_a_large_mutation_the_server_did_not_process_leaves_the_batch_budget(
    backend, client_for, mocker
):
    state, endpoint = backend
    state.replies = [envoy_503(ENVOY_REFUSED)]
    sizer = mocker.patch("kili.core.graphql.graphql_client.mutation_batch_sizer")

    client_for(endpoint).execute(
        "mutation($m: String) { appendManyAssets(data: {m: $m}) { id } }", {"m": LARGE}
    )

    assert len(state.bodies) == 2  # resent, since Envoy never forwarded it
    sizer.record_failure.assert_not_called()


def test_a_mutation_too_large_for_the_server_shrinks_the_batch_budget(backend, client_for, mocker):
    state, endpoint = backend
    state.replies = [envoy_503(b"")]  # reset after forwarding: may have been too heavy
    sizer = mocker.patch("kili.core.graphql.graphql_client.mutation_batch_sizer")

    with pytest.raises(MutationOutcomeUnknownError):
        client_for(endpoint).execute(
            "mutation($m: String) { appendManyAssets(data: {m: $m}) { id } }", {"m": LARGE}
        )

    sizer.record_failure.assert_called_once()


PAGE_QUERY = "query($first: Int, $skip: Int) { assets(first: $first, skip: $skip) { id } }"


def slow_to_start(handler: http.server.BaseHTTPRequestHandler) -> None:
    time.sleep(1)  # the server builds the page before the first byte
    body = json.dumps({"data": {"assets": [{"id": "x" * 200_000}]}}).encode()
    handler.send_response(200)
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def test_a_page_is_timed_on_its_download_not_on_the_server_work(backend, client_for, mocker):
    state, endpoint = backend
    state.replies = [slow_to_start]
    pages = mocker.patch("kili.core.graphql.graphql_client.query_page_sizer")

    client_for(endpoint).execute(PAGE_QUERY, {"first": 100, "skip": 0})

    response_bytes, seconds = pages.sizer.record_success.call_args.args
    assert response_bytes > 200_000
    assert seconds < 0.5  # the second the server took before answering is left out


def test_a_page_that_keeps_failing_shrinks_the_page_budget_once(backend, client_for, mocker):
    state, endpoint = backend
    state.replies = [envoy_503(b"")] * 3  # reset after forwarding: may have been too heavy
    pages = mocker.patch("kili.core.graphql.graphql_client.query_page_sizer")

    client_for(endpoint).execute(PAGE_QUERY, {"first": 100, "skip": 0})

    assert len(state.bodies) == 4  # retried, since it is a query
    pages.sizer.record_failure.assert_called_once()


def test_a_query_that_is_not_a_page_leaves_the_page_budget(backend, client_for, mocker):
    state, endpoint = backend
    state.replies = [envoy_503(b"")]
    pages = mocker.patch("kili.core.graphql.graphql_client.query_page_sizer")

    client_for(endpoint).execute("query { countAssets }")

    pages.sizer.record_failure.assert_not_called()
