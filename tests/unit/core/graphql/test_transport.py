import gzip

import pytest
import pytest_mock
from requests import PreparedRequest, Request, Response
from requests.adapters import HTTPAdapter
from requests.exceptions import ReadTimeout

from kili.core.graphql.transport import (
    COMPRESSION_THRESHOLD_BYTES,
    KiliHTTPAdapter,
    KiliRequestsHTTPTransport,
    scale_timeout,
)


def _request(body_bytes: int) -> PreparedRequest:
    return Request("POST", "https://kili/graphql", json={"q": "x" * body_bytes}).prepare()


def _response(status: int) -> Response:
    response = Response()
    response.status_code = status
    return response


@pytest.mark.parametrize(
    ("timeout", "body_bytes", "expected"),
    [
        (60, 0, (60, 60)),
        (60, 1_000, (60, 60.01)),
        (60, 20_000_000, (200, 260)),  # 200 s to upload, then the caller's 60 s for the server
        (120, 0, (120, 120)),
        ((5, 30), 0, (5, 30)),
        (None, 20_000_000, None),
    ],
)
def test_scale_timeout(timeout, body_bytes, expected):
    assert scale_timeout(timeout, body_bytes) == expected


def test_small_body_is_sent_as_is():
    request = _request(1_000)
    body = request.body

    KiliHTTPAdapter._compress(request)

    assert request.body == body
    assert "Content-Encoding" not in request.headers


def test_large_body_is_gzipped():
    request = _request(COMPRESSION_THRESHOLD_BYTES)
    raw = request.body
    assert isinstance(raw, bytes)

    payload_bytes = KiliHTTPAdapter._compress(request)

    assert payload_bytes == len(raw)
    assert request.headers["Content-Encoding"] == "gzip"
    assert isinstance(request.body, bytes)
    assert gzip.decompress(request.body) == raw
    assert request.headers["Content-Length"] == str(len(request.body))


def test_compression_can_be_disabled():
    request = _request(COMPRESSION_THRESHOLD_BYTES)

    KiliHTTPAdapter._compress(request, enabled=False)

    assert "Content-Encoding" not in request.headers


def test_a_transport_created_without_compression_sends_large_bodies_as_is():
    transport = KiliRequestsHTTPTransport(url="https://kili/graphql", compress_requests=False)

    assert transport.adapter.compress_requests is False


def test_send_scales_both_timeouts_to_the_compressed_body(
    mocker: pytest_mock.MockerFixture,
):
    send = mocker.patch.object(HTTPAdapter, "send", return_value=_response(200))
    request = _request(COMPRESSION_THRESHOLD_BYTES)

    KiliHTTPAdapter().send(request, timeout=60)

    connect, read = send.call_args.kwargs["timeout"]
    assert connect == 60
    assert read == pytest.approx(60, abs=0.1)  # a gzipped run of "x" is tiny


def test_send_measures_the_exchange(mocker: pytest_mock.MockerFixture):
    adapter = KiliHTTPAdapter()
    mocker.patch.object(HTTPAdapter, "send", return_value=_response(200))

    adapter.send(_request(500_000), timeout=60)

    exchange = adapter.last_exchange
    assert exchange is not None
    assert exchange.payload_bytes == len(_request(500_000).body)  # type: ignore
    assert exchange.succeeded


@pytest.mark.parametrize("status", [413, 429, 503])
def test_send_measures_an_error_status_as_a_failure(mocker: pytest_mock.MockerFixture, status: int):
    adapter = KiliHTTPAdapter()
    mocker.patch.object(HTTPAdapter, "send", return_value=_response(status))

    adapter.send(_request(500_000), timeout=60)

    assert adapter.last_exchange is not None
    assert not adapter.last_exchange.succeeded


def test_send_measures_a_request_that_raised(mocker: pytest_mock.MockerFixture):
    adapter = KiliHTTPAdapter()
    mocker.patch.object(HTTPAdapter, "send", side_effect=ReadTimeout())

    with pytest.raises(ReadTimeout):
        adapter.send(_request(500_000), timeout=60)

    assert adapter.last_exchange is not None
    assert adapter.last_exchange.payload_bytes > 500_000
    assert not adapter.last_exchange.succeeded


def test_a_redirect_that_drops_the_body_drops_its_encoding():
    request = _request(COMPRESSION_THRESHOLD_BYTES)
    KiliHTTPAdapter._compress(request)
    request.body = None  # what requests does on a 301/302

    KiliHTTPAdapter._compress(request)

    assert "Content-Encoding" not in request.headers


def test_transport_mounts_the_adapter_on_every_session():
    transport = KiliRequestsHTTPTransport(url="https://kili/graphql")

    for _ in range(2):  # gql opens and closes a session per operation
        transport.connect()
        assert transport.session is not None
        assert transport.session.get_adapter("https://kili/graphql") is transport.adapter
        transport.close()


def test_the_mounted_adapter_never_retries_by_itself():
    # even when asked to: gql's own retrying adapter must be replaced by the Kili one
    transport = KiliRequestsHTTPTransport(url="https://kili/graphql", retries=10)

    transport.connect()
    assert transport.session is not None
    adapter = transport.session.get_adapter("https://kili/graphql")
    transport.close()

    # a urllib3 retry would resend mutations behind the client's back
    assert adapter.max_retries.total == 0
    assert adapter.max_retries.read is False
