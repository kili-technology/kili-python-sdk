"""Mocks for the import_asset service test"""
from unittest.mock import MagicMock

mocked_request_signed_urls = MagicMock(
    side_effect=lambda _auth, filePaths: ["https://signed_url?id=id"] * len(filePaths)
)

mocked_upload_data_via_rest = MagicMock(side_effect=lambda signed_urls, _a, _b: signed_urls)

mocked_unique_id = MagicMock(return_value="unique_id")

mocked_auth = MagicMock()


def mocked_project_input_type(input_type: str):
    return lambda *_: [{"inputType": input_type}]
