"""Tests for asset formatters, specifically jsonResponseUrl optimization (LAB-4123).

This test file verifies that download_json_responses_parallel correctly:
- Downloads JSON from URLs in parallel
- Handles batching correctly
- Retries a failed download, then raises: never an empty jsonResponse in place of a label's (LAB-4963)
- Improves performance over sequential processing
"""

import asyncio
import io
import json
import pickle
import traceback
from unittest.mock import AsyncMock, Mock, patch

import pytest
import requests

from kili.adapters.http_client import HttpClient
from kili.adapters.kili_api_gateway.asset.formatters import (
    JSON_RESPONSE_BATCH_SIZE,
    _is_transient,
    download_json_responses_parallel,
    load_asset_json_fields,
)
from kili.adapters.kili_api_gateway.helpers.http_json import load_json_from_link
from kili.exceptions import JsonResponseDownloadError


class TestLoadJsonFromLink:
    """Test loading JSON from a URL."""

    def test_load_json_from_valid_url(self):
        """Test loading JSON from a valid URL."""
        http_client = Mock()
        response = Mock()
        response.json.return_value = {"key": "value"}
        http_client.get.return_value = response

        result = load_json_from_link("https://example.com/data.json", http_client)

        assert result == {"key": "value"}
        http_client.get.assert_called_once_with("https://example.com/data.json", timeout=30)

    def test_load_json_from_empty_string(self):
        """Test that empty string returns empty dict."""
        http_client = Mock()

        result = load_json_from_link("", http_client)

        assert result == {}
        http_client.get.assert_not_called()

    def test_load_json_from_non_url(self):
        """Test that non-URL string returns empty dict."""
        http_client = Mock()

        result = load_json_from_link("not-a-url", http_client)

        assert result == {}
        http_client.get.assert_not_called()


class TestDownloadJsonResponsesParallel:
    """Test parallel downloading of JSON responses."""

    def test_download_single_json_response(self):
        """Test downloading a single JSON response."""
        http_client = Mock()
        label = {"id": "label1", "jsonResponseUrl": "https://example.com/label1.json"}
        url_to_label_mapping = [("https://example.com/label1.json", label)]

        with patch(
            "kili.adapters.kili_api_gateway.asset.formatters._download_json_response",
            new_callable=AsyncMock,
        ) as mock_download:
            mock_download.return_value = {"annotation": "data"}

            download_json_responses_parallel(url_to_label_mapping, http_client)

            # Verify the JSON was downloaded and assigned
            assert label["jsonResponse"] == {"annotation": "data"}
            # Verify jsonResponseUrl was removed
            assert "jsonResponseUrl" not in label
            mock_download.assert_called_once()

    def test_download_multiple_json_responses(self):
        """Test downloading multiple JSON responses in parallel."""
        http_client = Mock()
        label1 = {"id": "label1", "jsonResponseUrl": "https://example.com/label1.json"}
        label2 = {"id": "label2", "jsonResponseUrl": "https://example.com/label2.json"}
        label3 = {"id": "label3", "jsonResponseUrl": "https://example.com/label3.json"}

        url_to_label_mapping = [
            ("https://example.com/label1.json", label1),
            ("https://example.com/label2.json", label2),
            ("https://example.com/label3.json", label3),
        ]

        # Create mock side effect for different URLs
        async def mock_download(url, client):
            if "label1" in url:
                return {"data": "label1"}
            elif "label2" in url:
                return {"data": "label2"}
            elif "label3" in url:
                return {"data": "label3"}
            return {}

        with patch(
            "kili.adapters.kili_api_gateway.asset.formatters._download_json_response",
            side_effect=mock_download,
        ):
            download_json_responses_parallel(url_to_label_mapping, http_client)

            # Verify all labels got their JSON
            assert label1["jsonResponse"] == {"data": "label1"}
            assert label2["jsonResponse"] == {"data": "label2"}
            assert label3["jsonResponse"] == {"data": "label3"}

            # Verify all URLs were removed
            assert "jsonResponseUrl" not in label1
            assert "jsonResponseUrl" not in label2
            assert "jsonResponseUrl" not in label3

    def test_download_processes_in_batches(self):
        """Test that downloads are processed in batches of JSON_RESPONSE_BATCH_SIZE."""
        http_client = Mock()
        # Create more labels than batch size
        num_labels = JSON_RESPONSE_BATCH_SIZE + 5
        labels = [
            {"id": f"label{i}", "jsonResponseUrl": f"https://example.com/label{i}.json"}
            for i in range(num_labels)
        ]
        url_to_label_mapping = [
            (f"https://example.com/label{i}.json", label) for i, label in enumerate(labels)
        ]

        # Mock the async download function
        with patch(
            "kili.adapters.kili_api_gateway.asset.formatters._download_json_response",
            new_callable=AsyncMock,
        ) as mock_download:
            mock_download.return_value = {"data": "test"}

            # Call the function
            download_json_responses_parallel(url_to_label_mapping, http_client)

            # Verify all labels got their JSON response
            for label in labels:
                assert label["jsonResponse"] == {"data": "test"}
                assert "jsonResponseUrl" not in label

            # Verify download was called for all URLs
            assert mock_download.call_count == num_labels

    def test_download_in_existing_event_loop(self):
        """Test that downloads work when called from within an existing event loop."""
        import asyncio

        http_client = Mock()
        label = {"id": "label1", "jsonResponseUrl": "https://example.com/label1.json"}
        url_to_label_mapping = [("https://example.com/label1.json", label)]

        # Mock the http_client.get response
        mock_response = Mock()
        mock_response.json.return_value = {"data": "test"}
        http_client.get.return_value = mock_response

        # Run inside an existing event loop (simulating Jupyter/FastAPI)
        async def run_in_loop():
            download_json_responses_parallel(url_to_label_mapping, http_client)

        asyncio.run(run_in_loop())

        # Verify the JSON was downloaded (sequentially in this case)
        assert label["jsonResponse"] == {"data": "test"}
        assert "jsonResponseUrl" not in label
        http_client.get.assert_called_once_with("https://example.com/label1.json", timeout=30)


class TestLoadAssetJsonFields:
    """Test load_asset_json_fields integration with download_json_responses_parallel."""

    def test_load_asset_with_latest_label_json_response_url(self):
        """Test loading asset with latestLabel.jsonResponseUrl."""
        http_client = Mock()

        asset = {
            "id": "asset1",
            "latestLabel": {
                "id": "label1",
                "jsonResponse": '{"old": "data"}',  # This should be replaced
                "jsonResponseUrl": "https://example.com/label1.json",
            },
        }

        fields = ["id", "latestLabel.jsonResponse", "latestLabel.jsonResponseUrl"]

        with patch(
            "kili.adapters.kili_api_gateway.asset.formatters._download_json_response",
            new_callable=AsyncMock,
        ) as mock_download:
            mock_download.return_value = {"annotation": "data"}

            result = load_asset_json_fields(asset, fields, http_client)

            # Verify URL was used instead of parsing string
            assert result["latestLabel"]["jsonResponse"] == {"annotation": "data"}
            assert "jsonResponseUrl" not in result["latestLabel"]
            mock_download.assert_called_once()

    def test_load_asset_with_labels_json_response_url(self):
        """Test loading asset with labels.jsonResponseUrl."""
        http_client = Mock()

        asset = {
            "id": "asset1",
            "labels": [
                {
                    "id": "label1",
                    "jsonResponse": '{"old": "data1"}',
                    "jsonResponseUrl": "https://example.com/label1.json",
                },
                {
                    "id": "label2",
                    "jsonResponse": '{"old": "data2"}',
                    "jsonResponseUrl": "https://example.com/label2.json",
                },
            ],
        }

        fields = ["id", "labels.jsonResponse", "labels.jsonResponseUrl"]

        # Create mock side effect for different URLs
        async def mock_download(url, client):
            if "label1" in url:
                return {"data": "label1"}
            elif "label2" in url:
                return {"data": "label2"}
            return {}

        with patch(
            "kili.adapters.kili_api_gateway.asset.formatters._download_json_response",
            side_effect=mock_download,
        ):
            result = load_asset_json_fields(asset, fields, http_client)

            # Verify URLs were used for both labels
            assert result["labels"][0]["jsonResponse"] == {"data": "label1"}
            assert result["labels"][1]["jsonResponse"] == {"data": "label2"}
            assert "jsonResponseUrl" not in result["labels"][0]
            assert "jsonResponseUrl" not in result["labels"][1]

    def test_load_asset_without_json_response_url_falls_back_to_parsing(self):
        """Test that assets without jsonResponseUrl fall back to string parsing."""
        http_client = Mock()

        asset = {
            "id": "asset1",
            "latestLabel": {
                "id": "label1",
                "jsonResponse": '{"annotation": "data"}',
                # No jsonResponseUrl field
            },
        }

        fields = ["id", "latestLabel.jsonResponse"]

        result = load_asset_json_fields(asset, fields, http_client)

        # Verify string was parsed (not URL downloaded)
        assert result["latestLabel"]["jsonResponse"] == {"annotation": "data"}
        http_client.get.assert_not_called()

    def test_load_asset_with_both_labels_and_latest_label(self):
        """Test loading asset with both labels and latestLabel having URLs."""
        http_client = Mock()

        asset = {
            "id": "asset1",
            "labels": [
                {"id": "label1", "jsonResponseUrl": "https://example.com/label1.json"},
                {"id": "label2", "jsonResponseUrl": "https://example.com/label2.json"},
            ],
            "latestLabel": {"id": "latest", "jsonResponseUrl": "https://example.com/latest.json"},
        }

        fields = [
            "id",
            "labels.jsonResponse",
            "labels.jsonResponseUrl",
            "latestLabel.jsonResponse",
            "latestLabel.jsonResponseUrl",
        ]

        # Create mock side effect for different URLs
        async def mock_download(url, client):
            if "label1" in url:
                return {"data": "label1"}
            elif "label2" in url:
                return {"data": "label2"}
            elif "latest" in url:
                return {"data": "latest"}
            return {}

        with patch(
            "kili.adapters.kili_api_gateway.asset.formatters._download_json_response",
            side_effect=mock_download,
        ):
            result = load_asset_json_fields(asset, fields, http_client)

            # Verify all were downloaded
            assert result["labels"][0]["jsonResponse"] == {"data": "label1"}
            assert result["labels"][1]["jsonResponse"] == {"data": "label2"}
            assert result["latestLabel"]["jsonResponse"] == {"data": "latest"}


SIGNED_PATH = "/bucket/projects/project1/assets/asset1/labels/label1.json"
SIGNED_URL = f"https://storage.example.com{SIGNED_PATH}?X-Goog-Signature=secret-signature&a=b"
OTHER_URL = "https://storage.example.com/bucket/projects/project1/assets/asset2/labels/label2.json"
ANNOTATIONS = {"OBJECT_DETECTION_JOB": {"annotations": [{"mid": "rect-1", "type": "rectangle"}]}}


def _response(status=200, body=None, url=SIGNED_URL, raw=None):
    """A real requests Response: raise_for_status names the URL, query included, as in production."""
    response = requests.Response()
    response.status_code = status
    response.reason = {200: "OK", 403: "Forbidden", 408: "Request Timeout"}.get(status, "Error")
    response.url = url
    response.raw = io.BytesIO(json.dumps(body).encode() if raw is None else raw)
    return response


def _dropped_connection(url=SIGNED_URL):
    """A ConnectionError worded as requests words one from urllib3: it names the URL's path and query."""
    path = url.split("storage.example.com", 1)[-1]
    return requests.ConnectionError(
        "HTTPSConnectionPool(host='storage.example.com', port=443): Max retries exceeded with url:"
        f" {path} (Caused by NewConnectionError('Failed to establish a new connection'))"
    )


def _run(path, function):
    """Run `function` with no event loop (asyncio.run) or inside a running one (Jupyter)."""
    if path == "asyncio.run":
        function()
        return

    async def in_running_loop():
        function()

    asyncio.run(in_running_loop())


def _download(path, url, http_client):
    label = {"jsonResponseUrl": url}
    _run(path, lambda: download_json_responses_parallel([(url, label)], http_client))
    return label


@pytest.fixture(autouse=True)
def no_retry_wait(mocker):
    """The retries' backoff, skipped."""
    return mocker.patch("tenacity.nap.time.sleep")


@pytest.mark.parametrize("path", ["asyncio.run", "running loop"])
class TestJsonResponseDownloadFailures:
    """A label's jsonResponse that fails to download is retried, then raises (LAB-4963)."""

    def test_a_download_failing_once_is_retried(self, path):
        http_client = Mock(spec=HttpClient)
        http_client.get.side_effect = [_dropped_connection(), _response(body=ANNOTATIONS)]

        label = _download(path, SIGNED_URL, http_client)

        assert label == {"jsonResponse": ANNOTATIONS}
        assert http_client.get.call_count == 2

    @pytest.mark.parametrize("status", [408, 429, 500, 503])
    def test_a_transient_http_error_is_retried(self, path, status):
        http_client = Mock(spec=HttpClient)
        http_client.get.side_effect = [_response(status), _response(body=ANNOTATIONS)]

        label = _download(path, SIGNED_URL, http_client)

        assert label == {"jsonResponse": ANNOTATIONS}

    def test_a_download_that_keeps_failing_raises_naming_the_label(self, path):
        def get(url, **_):
            if url == SIGNED_URL:
                raise _dropped_connection()
            return _response(body=ANNOTATIONS, url=url)

        http_client = Mock(spec=HttpClient)
        http_client.get.side_effect = get
        failing = {"jsonResponseUrl": SIGNED_URL}
        other = {"jsonResponseUrl": OTHER_URL}

        with pytest.raises(JsonResponseDownloadError) as raised:
            _run(
                path,
                lambda: download_json_responses_parallel(
                    [(SIGNED_URL, failing), (OTHER_URL, other)], http_client
                ),
            )

        error = raised.value
        assert (error.label_id, error.asset_id, error.attempts) == ("label1", "asset1", 3)
        assert isinstance(error.cause, requests.ConnectionError)
        assert "label label1 of asset asset1 (tried 3 times" in str(error)
        assert "Run the call again" in str(error)
        assert "jsonResponse" not in failing
        assert [c.args[0] for c in http_client.get.call_args_list].count(SIGNED_URL) == 3

    def test_a_client_error_is_not_retried(self, path):
        http_client = Mock(spec=HttpClient)
        http_client.get.return_value = _response(403)

        with pytest.raises(JsonResponseDownloadError) as raised:
            _download(path, SIGNED_URL, http_client)

        assert raised.value.attempts == 1
        assert "tried once" in str(raised.value)
        http_client.get.assert_called_once()

    def test_the_attempts_are_counted(self, path):
        http_client = Mock(spec=HttpClient)
        http_client.get.side_effect = [_response(503), _response(403)]

        with pytest.raises(JsonResponseDownloadError) as raised:
            _download(path, SIGNED_URL, http_client)

        assert raised.value.attempts == 2
        assert "tried 2 times" in str(raised.value)

    def test_an_unreadable_body_is_retried_then_raises(self, path):
        http_client = Mock(spec=HttpClient)
        http_client.get.return_value = _response(raw=b"<html>cut")

        with pytest.raises(JsonResponseDownloadError) as raised:
            _download(path, SIGNED_URL, http_client)

        assert raised.value.attempts == 3
        assert http_client.get.call_count == 3

    @pytest.mark.parametrize(
        "failure", [lambda: _response(403), _dropped_connection], ids=["403", "dropped"]
    )
    def test_the_signed_query_is_never_shown(self, path, failure):
        http_client = Mock(spec=HttpClient)
        http_client.get.side_effect = lambda *_, **__: _raise_or_return(failure())

        with pytest.raises(JsonResponseDownloadError) as raised:
            _download(path, SIGNED_URL, http_client)

        assert "secret-signature" in str(raised.value.cause)  # what requests says, kept on .cause
        shown = str(raised.value) + "".join(traceback.format_exception(raised.value))
        assert "secret-signature" not in shown
        assert SIGNED_PATH in str(raised.value)

    def test_a_stored_empty_json_response_stays_empty(self, path):
        http_client = Mock(spec=HttpClient)
        http_client.get.return_value = _response(body={})

        label = _download(path, SIGNED_URL, http_client)

        assert label == {"jsonResponse": {}}
        http_client.get.assert_called_once_with(SIGNED_URL, timeout=30)


def _raise_or_return(failure):
    if isinstance(failure, Exception):
        raise failure
    return failure


@pytest.mark.parametrize(
    ("error", "transient"),
    [
        (requests.ConnectionError("connection dropped"), True),
        (requests.ReadTimeout("read timed out"), True),
        (requests.exceptions.ChunkedEncodingError("body cut short"), True),
        (requests.exceptions.JSONDecodeError("Expecting value", "<html>", 0), True),
        (json.JSONDecodeError("Expecting value", "<html>", 0), True),
        (requests.HTTPError("no response"), True),
        (requests.HTTPError(response=_response(408)), True),
        (requests.HTTPError(response=_response(429)), True),
        (requests.HTTPError(response=_response(500)), True),
        (requests.HTTPError(response=_response(503)), True),
        (requests.HTTPError(response=_response(400)), False),
        (requests.HTTPError(response=_response(403)), False),
        (requests.HTTPError(response=_response(404)), False),
        (requests.exceptions.SSLError("certificate verify failed"), False),
        (requests.exceptions.InvalidURL("bad url"), False),
    ],
    ids=lambda value: value if isinstance(value, bool) else repr(value)[:40],
)
def test_what_is_retried(error, transient):
    assert _is_transient(error) is transient


class TestJsonResponseDownloadError:
    """The error names what the URL names, and survives a process pool."""

    def test_an_unknown_url_names_no_label(self, no_retry_wait):
        http_client = Mock(spec=HttpClient)
        url = "https://proxy.example.com/download?token=secret-token"
        http_client.get.side_effect = _dropped_connection(url)

        with pytest.raises(JsonResponseDownloadError) as raised:
            download_json_responses_parallel([(url, {"jsonResponseUrl": url})], http_client)

        assert (raised.value.label_id, raised.value.asset_id) == (None, None)
        assert "jsonResponse of a label" in str(raised.value)
        assert "secret-token" not in str(raised.value)
        assert no_retry_wait.call_count == 2

    def test_it_is_a_requests_exception_that_pickles(self):
        error = JsonResponseDownloadError("label1", "asset1", _dropped_connection(), 3)

        unpickled = pickle.loads(pickle.dumps(error))

        assert isinstance(unpickled, requests.RequestException)
        assert str(unpickled) == str(error)
        assert (unpickled.label_id, unpickled.asset_id, unpickled.attempts) == (
            "label1",
            "asset1",
            3,
        )


def test_load_asset_json_fields_raises_rather_than_return_an_empty_label():
    """An asset whose latest label cannot be downloaded raises from assets() (LAB-4963)."""
    http_client = Mock(spec=HttpClient)
    http_client.get.side_effect = _dropped_connection()
    asset = {"externalId": "img-1", "latestLabel": {"jsonResponseUrl": SIGNED_URL}}

    with pytest.raises(JsonResponseDownloadError, match="label label1 of asset asset1"):
        load_asset_json_fields(
            asset,
            ["externalId", "latestLabel.jsonResponse", "latestLabel.jsonResponseUrl"],
            http_client,
        )

    assert asset["latestLabel"] == {"jsonResponseUrl": SIGNED_URL}
