import shutil
import tempfile
from test.services.import_asset.mocks import (
    mocked__mutate_from_paginated_call,
    mocked_request_signed_urls,
    mocked_upload_data_via_rest,
)
from test.utils import LocalDownloader
from unittest import TestCase
from unittest.mock import ANY, patch

from kili.graphQL.operations.asset.mutations import (
    GQL_APPEND_MANY_FRAMES_TO_DATASET,
    GQL_APPEND_MANY_TO_DATASET,
)
from kili.services.import_asset import import_assets


@patch("kili.utils.bucket.request_signed_urls", mocked_request_signed_urls)
@patch("kili.utils.bucket.upload_data_via_rest", mocked_upload_data_via_rest)
@patch("kili.utils.pagination._mutate_from_paginated_call", mocked__mutate_from_paginated_call)
class PDFTestCase(TestCase):
    def setUp(self):
        self.input_type = "PDF"
        self.project_id = "pdf_project_id"
        self.auth = None
        self.test_dir = tempfile.mkdtemp()
        self.downloader = LocalDownloader(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_upload_from_one_local_pdf(self):
        url = (
            "https://storage.googleapis.com/label-public-staging/asset-test-sample/pdfs/sample.pdf"
        )
        path = self.downloader(url)
        assets = [{"content": path, "external_id": "local pdf file"}]
        import_assets(self.auth, self.input_type, self.project_id, assets)
        mocked__mutate_from_paginated_call.assert_called_with(
            ANY,
            {
                "content_array": ["https://signed_url"],
                "external_id_array": ["local pdf file"],
                "is_honeypot_array": [False],
                "json_content_array": [""],
                "json_metadata_array": ["{}"],
                "status_array": ["TODO"],
            },
            ANY,
            GQL_APPEND_MANY_TO_DATASET,
        )

    def test_upload_from_one_hosted_pdf(
        self,
    ):
        assets = [{"content": "https://hosted-data", "external_id": "hosted file"}]
        import_assets(self.auth, self.input_type, self.project_id, assets)
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
