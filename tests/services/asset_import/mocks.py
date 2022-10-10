"""Mocks for the import_asset service test"""
from unittest.mock import MagicMock

mocked_request_signed_urls = MagicMock(
    side_effect=lambda _auth, _project_id, size: ["https://signed_url?id=id"] * size
)

mocked_upload_data_via_rest = MagicMock(side_effect=lambda signed_urls, _a, _b: signed_urls)

mocked_auth = MagicMock()
