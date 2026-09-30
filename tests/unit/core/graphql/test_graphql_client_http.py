"""The GraphQL client against a local HTTP server, through the real transport, requests and urllib3."""

import http.server
import json
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

    def handle(self, handler: http.server.BaseHTTPRequestHandler) -> None:
        length = int(handler.headers["Content-Length"])
        self.bodies.append(handler.rfile.read(length))
        self.encodings.append(handler.headers.get("Content-Encoding"))
        reply = self.replies.pop(0) if self.replies else ok
        reply(handler)


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

    def build(endpoint: str) -> GraphQLClient:
        return GraphQLClient(
            endpoint=endpoint,
            api_key="key",
            client_name=GraphQLClientName.SDK,
            http_client=HttpClient(kili_endpoint=endpoint, api_key="key", verify=True),
            enable_schema_caching=False,
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
