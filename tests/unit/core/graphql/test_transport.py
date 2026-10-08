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
    rejects_compression,
    scale_timeout,
)


def _request(body_bytes: int) -> PreparedRequest:
    return Request("POST", "https://kili/graphql", json={"q": "x" * body_bytes}).prepare()


def _response(status: int, content: bytes = b"") -> Response:
    response = Response()
    response.status_code = status
    response._content = content  # pylint: disable=protected-access
    response.encoding = "utf-8"
    return response


def _recording_send(mocker: pytest_mock.MockerFixture, *responses: Response) -> list[dict]:
    """Patch the base adapter to answer these responses, recording each request as sent."""
    sent: list[dict] = []
    answers = iter(responses)

    def send(_adapter, request, **_kwargs):
        sent.append({"body": request.body, "headers": dict(request.headers)})
        return next(answers)

    mocker.patch.object(HTTPAdapter, "send", autospec=True, side_effect=send)
    return sent


# what express answers when a proxy dropped Content-Encoding and forwarded the gzipped bytes
EXPRESS_PARSE_ERROR = (
    b"<!DOCTYPE html><html><body><pre>SyntaxError: Unexpected token</pre></body></html>"
)
GRAPHQL_ERROR = b'{"errors": [{"message": "Cannot query field"}]}'


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
    response = _response(200)
    response._content = b"r" * 1234  # pylint: disable=protected-access
    mocker.patch.object(HTTPAdapter, "send", return_value=response)

    adapter.send(_request(500_000), timeout=60)

    exchange = adapter.last_exchange
    assert exchange is not None
    assert exchange.payload_bytes == len(_request(500_000).body)  # type: ignore
    assert exchange.response_bytes == 1234
    assert 0 <= exchange.download_seconds <= exchange.seconds
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


@pytest.mark.parametrize(
    ("status", "content", "expected"),
    [
        (415, b"Unsupported Media Type", True),
        (400, EXPRESS_PARSE_ERROR, True),
        (400, b"", True),
        (400, b'{"message": "bad request"}', True),
        (400, GRAPHQL_ERROR, False),
        (400, b'{"data": null}', False),
        (200, b'{"data": {}}', False),
        (413, b"too large", False),
        (500, b"<html></html>", False),
    ],
)
def test_rejects_compression(status: int, content: bytes, expected: bool):
    assert rejects_compression(_response(status, content)) is expected


@pytest.mark.parametrize(
    "refusal", [_response(415, b"Unsupported Media Type"), _response(400, EXPRESS_PARSE_ERROR)]
)
def test_a_refused_compressed_request_is_sent_again_uncompressed_and_compression_stops(
    mocker: pytest_mock.MockerFixture, refusal: Response
):
    warning = mocker.patch("kili.core.graphql.transport.logger.warning")
    sent = _recording_send(mocker, refusal, _response(200, b'{"data": {}}'), _response(200))
    adapter = KiliHTTPAdapter()
    request = _request(COMPRESSION_THRESHOLD_BYTES)
    raw = request.body
    assert isinstance(raw, bytes)

    response = adapter.send(request, timeout=60)

    assert response.status_code == 200
    assert [s["headers"].get("Content-Encoding") for s in sent] == ["gzip", None]
    assert sent[1]["body"] == raw
    assert sent[1]["headers"]["Content-Length"] == str(len(raw))
    assert adapter.compress_requests is False
    assert adapter.last_exchange is not None
    assert adapter.last_exchange.succeeded
    warning.assert_called_once()
    assert "disable_request_compression=True" in warning.call_args.args[0]

    adapter.send(_request(COMPRESSION_THRESHOLD_BYTES), timeout=60)

    assert len(sent) == 3
    assert "Content-Encoding" not in sent[2]["headers"]


def test_compression_stays_on_when_the_uncompressed_request_is_refused_too(
    mocker: pytest_mock.MockerFixture,
):
    # the encoding was not what the proxy refused: compressing is not to blame
    warning = mocker.patch("kili.core.graphql.transport.logger.warning")
    sent = _recording_send(mocker, _response(415), _response(415))
    adapter = KiliHTTPAdapter()

    response = adapter.send(_request(COMPRESSION_THRESHOLD_BYTES), timeout=60)

    assert response.status_code == 415
    assert len(sent) == 2
    assert adapter.compress_requests is True
    warning.assert_not_called()


@pytest.mark.parametrize(
    ("body_bytes", "answer"),
    [
        (1_000, _response(415)),  # not compressed: nothing to take back
        (COMPRESSION_THRESHOLD_BYTES, _response(400, GRAPHQL_ERROR)),  # parsed, then refused
        (COMPRESSION_THRESHOLD_BYTES, _response(413)),
    ],
)
def test_other_failures_are_not_sent_again(
    mocker: pytest_mock.MockerFixture, body_bytes: int, answer: Response
):
    sent = _recording_send(mocker, answer)
    adapter = KiliHTTPAdapter()

    response = adapter.send(_request(body_bytes), timeout=60)

    assert response is answer
    assert len(sent) == 1
    assert adapter.compress_requests is True
