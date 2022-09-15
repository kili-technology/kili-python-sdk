import shutil
import tempfile
from test.services.asset_import.mocks import (
    mocked__mutate_from_paginated_call,
    mocked_request_signed_urls,
    mocked_upload_data_via_rest,
)
from test.utils import LocalDownloader
from unittest import TestCase
from unittest.mock import ANY, MagicMock, patch

from kili.graphql.operations.asset.mutations import GQL_APPEND_MANY_TO_DATASET
from kili.queries.project import QueriesProject
from kili.services.asset_import import import_assets
from kili.services.asset_import.base import BatchImporter

mocked_execute_throttle_call = MagicMock()


@patch("kili.utils.bucket.request_signed_urls", mocked_request_signed_urls)
@patch("kili.utils.bucket.upload_data_via_rest", mocked_upload_data_via_rest)
@patch("kili.utils.pagination.execute_throttle_call", mocked_execute_throttle_call)
@patch.object(
    QueriesProject,
    "projects",
    MagicMock(return_value=[{"inputType": "PDF"}]),
)
class PDFTestCase(TestCase):
    def setUp(self):
        self.project_id = "project_id"
        self.test_dir = tempfile.mkdtemp()
        self.downloader = LocalDownloader(self.test_dir)
        self.auth = None

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_upload_from_one_local_pdf(self):
        url = (
            "https://storage.googleapis.com/label-public-staging/asset-test-sample/pdfs/sample.pdf"
        )
        path = self.downloader(url)
        assets = [{"content": path, "external_id": "local pdf file"}]
        import_assets(self.auth, self.project_id, assets)
        mocked_execute_throttle_call.assert_called_with(
            ANY,
            GQL_APPEND_MANY_TO_DATASET,
            {
                "data": {
                    "contentArray": ["https://signed_url"],
                    "externalIDArray": ["local pdf file"],
                    "isHoneypotArray": [False],
                    "jsonContentArray": [""],
                    "jsonMetadataArray": ["{}"],
                    "statusArray": ["TODO"],
                },
                "where": {"id": self.project_id},
            },
        )

    def test_upload_from_one_hosted_pdf(
        self,
    ):
        assets = [{"content": "https://hosted-data", "external_id": "hosted file"}]
        import_assets(self.auth, self.project_id, assets)
        mocked_execute_throttle_call.assert_called_with(
            ANY,
            GQL_APPEND_MANY_TO_DATASET,
            {
                "data": {
                    "contentArray": ["https://hosted-data"],
                    "externalIDArray": ["hosted file"],
                    "isHoneypotArray": [False],
                    "jsonContentArray": [""],
                    "jsonMetadataArray": ["{}"],
                    "statusArray": ["TODO"],
                },
                "where": {"id": self.project_id},
            },
        )
