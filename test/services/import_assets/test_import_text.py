import shutil
import tempfile
from test.services.import_assets.mocks import (
    mocked__mutate_from_paginated_call,
    mocked_request_signed_urls,
    mocked_upload_data_via_rest,
)
from test.utils import LocalDownloader
from unittest import TestCase
from unittest.mock import ANY, MagicMock, patch

from kili.graphql.operations.asset.mutations import GQL_APPEND_MANY_TO_DATASET
from kili.queries.project import QueriesProject
from kili.services.import_assets import import_assets


@patch("kili.utils.bucket.request_signed_urls", mocked_request_signed_urls)
@patch("kili.utils.bucket.upload_data_via_rest", mocked_upload_data_via_rest)
@patch("kili.utils.pagination._mutate_from_paginated_call", mocked__mutate_from_paginated_call)
@patch.object(
    QueriesProject,
    "projects",
    MagicMock(return_value=[{"inputType": "TEXT"}]),
)
class TextTestCase(TestCase):
    def setUp(self):
        self.project_id = "project_id"
        self.test_dir = tempfile.mkdtemp()
        self.downloader = LocalDownloader(self.test_dir)
        self.auth = None

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_upload_from_one_local_text_file(self):
        url = "https://storage.googleapis.com/label-public-staging/asset-test-sample/texts/test_text_file.txt"
        path = self.downloader(url)
        assets = [{"content": path, "external_id": "local text file"}]
        import_assets(self.auth, self.project_id, assets)
        mocked__mutate_from_paginated_call.assert_called_with(
            ANY,
            {
                "content_array": ["https://signed_url"],
                "external_id_array": ["local text file"],
                "is_honeypot_array": [False],
                "json_content_array": [""],
                "json_metadata_array": ["{}"],
                "status_array": ["TODO"],
            },
            ANY,
            GQL_APPEND_MANY_TO_DATASET,
        )

    def test_upload_from_one_hosted_text_file(
        self,
    ):
        assets = [{"content": "https://hosted-data", "external_id": "hosted file"}]
        import_assets(self.auth, self.project_id, assets)
        mocked__mutate_from_paginated_call.assert_called_with(
            ANY,
            {
                "content_array": ["https://hosted-data"],
                "external_id_array": ["hosted file"],
                "is_honeypot_array": [False],
                "json_content_array": [""],
                "json_metadata_array": ["{}"],
                "status_array": ["TODO"],
            },
            ANY,
            GQL_APPEND_MANY_TO_DATASET,
        )

    def test_upload_from_raw_text(self):
        assets = [{"content": "this is raw text", "external_id": "raw text"}]
        import_assets(self.auth, self.project_id, assets)
        mocked__mutate_from_paginated_call.assert_called_with(
            ANY,
            {
                "content_array": ["https://signed_url"],
                "external_id_array": ["raw text"],
                "is_honeypot_array": [False],
                "json_content_array": [""],
                "json_metadata_array": ["{}"],
                "status_array": ["TODO"],
            },
            ANY,
            GQL_APPEND_MANY_TO_DATASET,
        )

    def test_upload_from_one_rich_text(self):
        json_content = [
            {
                "children": [
                    {
                        "id": "1",
                        "underline": True,
                        "text": "A rich text asset",
                    }
                ]
            }
        ]
        assets = [{"json_content": json_content, "external_id": "rich text"}]
        import_assets(self.auth, self.project_id, assets)
        stringify_json_content = (
            '[{"children": [{"id": "1", "underline": true, "text": "A rich text asset"}]}]'
        )
        mocked__mutate_from_paginated_call.assert_called_with(
            ANY,
            {
                "content_array": [""],
                "external_id_array": ["rich text"],
                "is_honeypot_array": [False],
                "json_content_array": [stringify_json_content],
                "json_metadata_array": ["{}"],
                "status_array": ["TODO"],
            },
            ANY,
            GQL_APPEND_MANY_TO_DATASET,
        )
