import contextlib
import datetime
import socket
import socketserver
import ssl
import threading
from collections.abc import Iterator

import pytest
import requests
from gql import gql
from gql.transport import exceptions
from requests.exceptions import ChunkedEncodingError, ReadTimeout, SSLError
from requests.exceptions import ConnectionError as RequestsConnectionError
from urllib3.exceptions import ProtocolError, ReadTimeoutError

from kili.core.graphql.retry import (
    Outcome,
    attempts_allowed,
    classify,
    describe,
    is_mutation,
    operation_name,
    parse_retry_after,
    retry_after_seconds,
    should_retry,
)


def _raised(function, *args, **kwargs) -> BaseException:
    try:
        function(*args, **kwargs)
    except BaseException as error:  # pylint: disable=broad-exception-caught
        return error
    raise AssertionError("expected an error")


def _closed_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture(scope="module")
def dropping_proxy() -> Iterator[str]:
    """A proxy that reads the whole request, then closes the connection without answering."""

    class Handler(socketserver.BaseRequestHandler):
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
            self.request.close()

    server = socketserver.ThreadingTCPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()


@pytest.fixture(scope="module")
def forbidding_proxy() -> Iterator[str]:
    """A proxy that refuses every CONNECT tunnel."""

    class Handler(socketserver.BaseRequestHandler):
        def handle(self):
            self.request.recv(4096)
            self.request.sendall(b"HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\n\r\n")

    server = socketserver.TCPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()


def _stalled_body() -> RequestsConnectionError:
    """What requests raises when the answer stalls after its headers."""
    return RequestsConnectionError(ReadTimeoutError(None, "/graphql", "Read timed out."))  # type: ignore


def _server_error(code: int, body: str = "", headers=None) -> exceptions.TransportServerError:
    """A TransportServerError as gql raises it: from the requests HTTPError of the response."""
    response = requests.Response()
    response.status_code = code
    response._content = body.encode()  # pylint: disable=protected-access
    response.headers.update(headers or {})
    try:
        raise exceptions.TransportServerError(f"{code} Server Error", code) from requests.HTTPError(
            response=response
        )
    except exceptions.TransportServerError as error:
        return error


ENVOY_REFUSED = (
    "upstream connect error or disconnect/reset before headers. reset reason: remote connection"
    " failure, transport failure reason: delayed connect error: Connection refused"
)
ENVOY_RESET_AFTER_FORWARD = (
    "upstream connect error or disconnect/reset before headers. reset reason: connection"
    " termination"
)
# when Envoy retries itself, its last attempt may fail to connect after an earlier one forwarded
ENVOY_RETRIED_AFTER_FORWARD = (
    "upstream connect error or disconnect/reset before headers. retried and the latest reset"
    " reason: remote connection failure, transport failure reason: delayed connect error"
)
FLAGSMITH_ERROR = exceptions.TransportQueryError(
    "Invalid request made to Flagsmith API. Response status code: 502"
)
VALIDATION_ERROR = exceptions.TransportQueryError(
    'Variable "$skip" of required type "Int!" was not provided.'
)


def test_a_refused_connection_was_not_processed():
    error = _raised(requests.post, f"http://127.0.0.1:{_closed_port()}/graphql", timeout=2)

    assert isinstance(error, RequestsConnectionError)
    assert classify(error) is Outcome.NOT_PROCESSED


def test_a_refused_connection_to_the_proxy_was_not_processed():
    proxy = f"http://127.0.0.1:{_closed_port()}"
    error = _raised(requests.get, "http://kili.invalid/graphql", proxies={"http": proxy}, timeout=2)

    assert isinstance(error, requests.exceptions.ProxyError)
    assert classify(error) is Outcome.NOT_PROCESSED


def test_a_tunnel_the_proxy_refuses_was_not_processed(forbidding_proxy: str):
    error = _raised(
        requests.get, "https://kili.invalid/graphql", proxies={"https": forbidding_proxy}, timeout=2
    )

    assert isinstance(error, requests.exceptions.ProxyError)
    assert classify(error) is Outcome.NOT_PROCESSED


def _read_request(sock) -> bytes:
    data = b""
    while b"\r\n\r\n" not in data:
        data += sock.recv(65536)
    head, _, body = data.partition(b"\r\n\r\n")
    length = next(
        int(line.split(b":")[1])
        for line in head.split(b"\r\n")
        if line.lower().startswith(b"content-length")
    )
    while len(body) < length:
        body += sock.recv(65536)
    return body


@pytest.fixture(scope="module")
def https_server_that_drops(tmp_path_factory) -> Iterator[int]:
    """An HTTPS server that reads the whole request, then closes without answering."""
    x509 = pytest.importorskip("cryptography.x509")
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec

    key = ec.generate_private_key(ec.SECP256R1())
    name = x509.Name([x509.NameAttribute(x509.oid.NameOID.COMMON_NAME, "localhost")])
    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(1)
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=1))
        .sign(key, hashes.SHA256())
    )
    directory = tmp_path_factory.mktemp("tls")
    (directory / "cert.pem").write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    (directory / "key.pem").write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(directory / "cert.pem", directory / "key.pem")

    class Handler(socketserver.BaseRequestHandler):
        def handle(self):
            with context.wrap_socket(self.request, server_side=True) as tls:
                _read_request(tls)

    server = socketserver.ThreadingTCPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield server.server_address[1]
    server.shutdown()


@pytest.fixture(scope="module")
def tunnelling_proxy() -> Iterator[str]:
    """A proxy that opens CONNECT tunnels to localhost."""

    class Handler(socketserver.BaseRequestHandler):
        def handle(self):
            request = b""
            while b"\r\n\r\n" not in request:
                request += self.request.recv(4096)
            port = int(request.split(b" ")[1].split(b":")[1])
            upstream = socket.create_connection(("127.0.0.1", port))
            self.request.sendall(b"HTTP/1.1 200 Connection established\r\n\r\n")

            def pipe(source, target):
                try:
                    while chunk := source.recv(65536):
                        target.sendall(chunk)
                except OSError:
                    pass
                finally:
                    # shutdown, not just close: on Linux, closing a socket another thread is
                    # reading does not send the FIN, so the client would wait for its timeout
                    with contextlib.suppress(OSError):
                        target.shutdown(socket.SHUT_RDWR)
                    target.close()

            threading.Thread(target=pipe, args=(upstream, self.request), daemon=True).start()
            pipe(self.request, upstream)

    server = socketserver.ThreadingTCPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()


def test_a_tunnel_that_drops_after_the_request_went_through_is_unknown(
    https_server_that_drops: int, tunnelling_proxy: str
):
    error = _raised(
        requests.post,
        f"https://localhost:{https_server_that_drops}/graphql",
        data=b"x" * 50_000,
        proxies={"https": tunnelling_proxy},
        verify=False,
        timeout=3,
    )

    assert isinstance(error, requests.exceptions.ProxyError)
    assert classify(error) is Outcome.UNKNOWN


def test_a_connection_that_drops_after_the_request_went_through_the_proxy_is_unknown(
    dropping_proxy: str,
):
    error = _raised(
        requests.post,
        "http://kili.invalid/graphql",
        data=b"x" * 50_000,
        proxies={"http": dropping_proxy},
        timeout=3,
    )

    # urllib3 reports it as a ProxyError, like a proxy it could not reach
    assert isinstance(error, requests.exceptions.ProxyError)
    assert classify(error) is Outcome.UNKNOWN


@pytest.mark.parametrize(
    "build",
    [
        lambda: requests.Request(
            "POST", "http://kili/graphql", json={"mark": float("nan")}
        ).prepare(),
        lambda: requests.Request("POST", "kili/graphql").prepare(),
        lambda: requests.post("ftp://kili/graphql", timeout=1),
    ],
    ids=["nan in the variables", "missing scheme", "unsupported scheme"],
)
def test_an_invalid_request_failed_before_being_sent(build):
    error = _raised(build)

    assert isinstance(error, requests.RequestException)
    assert classify(error) is Outcome.FAILED


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (_server_error(401), Outcome.NOT_PROCESSED),
        (_server_error(429), Outcome.NOT_PROCESSED),
        (_server_error(503, ENVOY_REFUSED), Outcome.NOT_PROCESSED),
        (_server_error(503, "no healthy upstream"), Outcome.NOT_PROCESSED),
        (_server_error(503, "reset reason: overflow"), Outcome.NOT_PROCESSED),
        (_server_error(503, "", {"Retry-After": "5"}), Outcome.UNKNOWN),
        (_server_error(503, ENVOY_RESET_AFTER_FORWARD), Outcome.UNKNOWN),
        (_server_error(503, ENVOY_RETRIED_AFTER_FORWARD), Outcome.UNKNOWN),
        (_server_error(503), Outcome.UNKNOWN),
        (_server_error(521), Outcome.NOT_PROCESSED),
        (_server_error(522), Outcome.UNKNOWN),
        (_server_error(500), Outcome.UNKNOWN),
        (_server_error(502), Outcome.UNKNOWN),
        (_server_error(504), Outcome.UNKNOWN),
        (_server_error(520), Outcome.UNKNOWN),
        (_server_error(400), Outcome.FAILED),
        (_server_error(413), Outcome.FAILED),
        (exceptions.TransportServerError("503 without a response", 503), Outcome.UNKNOWN),
        (ReadTimeout(), Outcome.UNKNOWN),
        (RequestsConnectionError(ProtocolError("Connection aborted.")), Outcome.UNKNOWN),
        (ChunkedEncodingError(), Outcome.UNKNOWN),
        (exceptions.TransportProtocolError("not a GraphQL result"), Outcome.UNKNOWN),
        (SSLError("EOF occurred in violation of protocol"), Outcome.UNKNOWN),
        (SSLError("[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed"), Outcome.FAILED),
        (FLAGSMITH_ERROR, Outcome.TRANSIENT),
        (VALIDATION_ERROR, Outcome.FAILED),
        (ValueError(), Outcome.FAILED),
    ],
)
def test_classify(error: BaseException, expected: Outcome):
    assert classify(error) is expected


@pytest.mark.parametrize(
    ("error", "query_attempts", "mutation_attempts"),
    [
        (_server_error(429), None, None),  # until the deadline
        (ReadTimeout(), 2, 1),  # a query that did not answer in time: one more try at most
        (_stalled_body(), 2, 1),  # the same, when the answer stalls after its headers
        (_server_error(502), 5, 1),
        (_server_error(500), 1, 1),  # the server failed: resending makes it fail again
        (_server_error(504), 2, 1),  # a gateway gave up on heavy work: one more try at most
        (_server_error(524), 2, 1),
        (VALIDATION_ERROR, 1, 1),
    ],
)
def test_attempts_allowed(error: BaseException, query_attempts, mutation_attempts):
    assert attempts_allowed(error, mutation=False) == query_attempts
    assert attempts_allowed(error, mutation=True) == mutation_attempts


@pytest.mark.parametrize(
    ("error", "retry_query", "retry_mutation"),
    [
        (_server_error(429), True, True),
        (_server_error(503, ENVOY_REFUSED), True, True),
        (_server_error(503, ENVOY_RESET_AFTER_FORWARD), True, False),
        (ReadTimeout(), True, False),
        (_server_error(502), True, False),
        (_server_error(500), False, False),
        (FLAGSMITH_ERROR, True, False),
        (VALIDATION_ERROR, False, False),
    ],
)
def test_should_retry(error: BaseException, retry_query: bool, retry_mutation: bool):
    assert should_retry(error, mutation=False) is retry_query
    assert should_retry(error, mutation=True) is retry_mutation


def test_retry_after_is_read_from_the_failed_response():
    assert retry_after_seconds(_server_error(429, "", {"Retry-After": "7"})) == 7.0
    assert retry_after_seconds(_server_error(429)) is None
    assert retry_after_seconds(ReadTimeout()) is None


@pytest.mark.parametrize(
    ("header", "expected"),
    [("12", 12.0), ("0.5", 0.5), ("3600", 60.0), ("-1", 0.0), (None, None), ("Wed, 21 Oct", None)],
)
def test_parse_retry_after(header, expected):
    assert parse_retry_after(header) == expected


def test_is_mutation_operation_name_and_describe():
    mutation = gql("mutation { appendManyAssets(data: {}) { id } }")
    query = gql("query { projects { id } }")

    assert is_mutation(mutation)
    assert not is_mutation(query)
    assert operation_name(mutation) == "appendManyAssets"
    assert operation_name(query) == "projects"
    assert describe(_server_error(503)) == "HTTP 503"
    assert describe(ReadTimeout()) == "ReadTimeout"
