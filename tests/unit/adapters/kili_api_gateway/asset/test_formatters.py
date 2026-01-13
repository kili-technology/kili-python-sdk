"""Tests for asset formatters, specifically jsonResponseUrl optimization (LAB-4123).

This test file verifies that download_json_responses_parallel correctly:
- Downloads JSON from URLs in parallel
- Handles batching correctly
- Handles errors gracefully
- Improves performance over sequential processing
"""

from unittest.mock import AsyncMock, Mock, patch

from kili.adapters.kili_api_gateway.asset.formatters import (
    JSON_RESPONSE_BATCH_SIZE,
    download_json_responses_parallel,
    load_asset_json_fields,
    load_json_from_link,
)


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
        label = {"id": "label1", "jsonResponseUrl": "https://example.com/label1.json"}
        url_to_label_mapping = [("https://example.com/label1.json", label)]

        with patch(
            "kili.adapters.kili_api_gateway.asset.formatters._download_json_response",
            new_callable=AsyncMock,
        ) as mock_download:
            mock_download.return_value = {"annotation": "data"}

            download_json_responses_parallel(url_to_label_mapping)

            # Verify the JSON was downloaded and assigned
            assert label["jsonResponse"] == {"annotation": "data"}
            # Verify jsonResponseUrl was removed
            assert "jsonResponseUrl" not in label
            mock_download.assert_called_once()

    def test_download_multiple_json_responses(self):
        """Test downloading multiple JSON responses in parallel."""
        label1 = {"id": "label1", "jsonResponseUrl": "https://example.com/label1.json"}
        label2 = {"id": "label2", "jsonResponseUrl": "https://example.com/label2.json"}
        label3 = {"id": "label3", "jsonResponseUrl": "https://example.com/label3.json"}

        url_to_label_mapping = [
            ("https://example.com/label1.json", label1),
            ("https://example.com/label2.json", label2),
            ("https://example.com/label3.json", label3),
        ]

        # Create mock side effect for different URLs
        async def mock_download(url):
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
            download_json_responses_parallel(url_to_label_mapping)

            # Verify all labels got their JSON
            assert label1["jsonResponse"] == {"data": "label1"}
            assert label2["jsonResponse"] == {"data": "label2"}
            assert label3["jsonResponse"] == {"data": "label3"}

            # Verify all URLs were removed
            assert "jsonResponseUrl" not in label1
            assert "jsonResponseUrl" not in label2
            assert "jsonResponseUrl" not in label3

    def test_download_handles_request_exception(self):
        """Test that request exceptions are handled gracefully."""
        label = {"id": "label1", "jsonResponseUrl": "https://example.com/label1.json"}
        url_to_label_mapping = [("https://example.com/label1.json", label)]

        # Mock download to raise httpx.HTTPError
        with patch(
            "kili.adapters.kili_api_gateway.asset.formatters._download_json_response",
            new_callable=AsyncMock,
        ) as mock_download:
            mock_download.return_value = {}  # Returns empty dict on error

            # Should not raise exception
            download_json_responses_parallel(url_to_label_mapping)

            # Should set empty dict on error
            assert label["jsonResponse"] == {}
            assert "jsonResponseUrl" not in label

    def test_download_handles_json_decode_error(self):
        """Test that JSON decode errors are handled gracefully."""
        label = {"id": "label1", "jsonResponseUrl": "https://example.com/label1.json"}
        url_to_label_mapping = [("https://example.com/label1.json", label)]

        # Mock download to return empty dict (simulating error)
        with patch(
            "kili.adapters.kili_api_gateway.asset.formatters._download_json_response",
            new_callable=AsyncMock,
        ) as mock_download:
            mock_download.return_value = {}  # Returns empty dict on error

            # Should not raise exception
            download_json_responses_parallel(url_to_label_mapping)

            # Should set empty dict on error
            assert label["jsonResponse"] == {}
            assert "jsonResponseUrl" not in label

    def test_download_handles_timeout_error(self):
        """Test that timeout errors are handled gracefully."""
        label = {"id": "label1", "jsonResponseUrl": "https://example.com/label1.json"}
        url_to_label_mapping = [("https://example.com/label1.json", label)]

        # Mock download to return empty dict (simulating error)
        with patch(
            "kili.adapters.kili_api_gateway.asset.formatters._download_json_response",
            new_callable=AsyncMock,
        ) as mock_download:
            mock_download.return_value = {}  # Returns empty dict on error

            # Should not raise exception
            download_json_responses_parallel(url_to_label_mapping)

            # Should set empty dict on error
            assert label["jsonResponse"] == {}
            assert "jsonResponseUrl" not in label

    def test_download_processes_in_batches(self):
        """Test that downloads are processed in batches of JSON_RESPONSE_BATCH_SIZE."""
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
            download_json_responses_parallel(url_to_label_mapping)

            # Verify all labels got their JSON response
            for label in labels:
                assert label["jsonResponse"] == {"data": "test"}
                assert "jsonResponseUrl" not in label

            # Verify download was called for all URLs
            assert mock_download.call_count == num_labels

    def test_download_mixed_success_and_failure(self):
        """Test downloading with some successes and some failures."""
        label_success = {"id": "success", "jsonResponseUrl": "https://example.com/success.json"}
        label_fail = {"id": "fail", "jsonResponseUrl": "https://example.com/fail.json"}

        url_to_label_mapping = [
            ("https://example.com/success.json", label_success),
            ("https://example.com/fail.json", label_fail),
        ]

        # Create mock side effect for different URLs
        async def mock_download(url):
            if "success" in url:
                return {"status": "ok"}
            return {}  # Failure returns empty dict

        with patch(
            "kili.adapters.kili_api_gateway.asset.formatters._download_json_response",
            side_effect=mock_download,
        ):
            download_json_responses_parallel(url_to_label_mapping)

            # Success should have data
            assert label_success["jsonResponse"] == {"status": "ok"}
            assert "jsonResponseUrl" not in label_success

            # Failure should have empty dict
            assert label_fail["jsonResponse"] == {}
            assert "jsonResponseUrl" not in label_fail


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
        async def mock_download(url):
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
        async def mock_download(url):
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
