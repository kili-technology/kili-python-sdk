import shutil
import tempfile
from test.services.asset_import.mocks import mocked_auth
from test.utils import LocalDownloader
from unittest import TestCase
from unittest.mock import call

from kili.graphql.operations.asset.mutations import (
    GQL_APPEND_MANY_FRAMES_TO_DATASET,
    GQL_APPEND_MANY_TO_DATASET,
)
from kili.services.asset_import import import_assets


class ImportTestCase(TestCase):
    def setUp(self):
        self.project_id = "project_id"
        self.test_dir = tempfile.mkdtemp()
        self.downloader = LocalDownloader(self.test_dir)
        self.auth = mocked_auth

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def get_expected_sync_call(
        self,
        content_array,
        external_id_array,
        is_honeypot_array,
        json_content_array,
        json_metadata_array,
        status_array,
    ):
        return (
            GQL_APPEND_MANY_TO_DATASET,
            {
                "data": {
                    "contentArray": content_array,
                    "externalIDArray": external_id_array,
                    "isHoneypotArray": is_honeypot_array,
                    "statusArray": status_array,
                    "jsonContentArray": json_content_array,
                    "jsonMetadataArray": json_metadata_array,
                },
                "where": {"id": self.project_id},
            },
        )

    def get_expected_async_call(
        self, content_array, external_id_array, json_metadata_array, upload_type
    ):
        return (
            GQL_APPEND_MANY_FRAMES_TO_DATASET,
            {
                "data": {
                    "contentArray": content_array,
                    "externalIDArray": external_id_array,
                    "jsonMetadataArray": json_metadata_array,
                    "uploadType": upload_type,
                },
                "where": {"id": self.project_id},
            },
        )

    def assert_upload_several_batches(self):
        nb_asset_test = 15
        external_id_array = [f"hosted file {i}" for i in range(nb_asset_test)]
        assets = [
            {"content": "https://hosted-data", "external_id": external_id}
            for external_id in external_id_array
        ]
        import_assets(self.auth, self.project_id, assets)
        expected_parameters_1 = self.get_expected_sync_call(
            ["https://hosted-data"] * 10,
            [external_id_array[i] for i in range(10)],
            [False] * 10,
            [""] * 10,
            ["{}"] * 10,
            ["TODO"] * 10,
        )
        expected_parameters_2 = self.get_expected_sync_call(
            ["https://hosted-data"] * 5,
            [external_id_array[i] for i in range(10, 15)],
            [False] * 5,
            [""] * 5,
            ["{}"] * 5,
            ["TODO"] * 5,
        )
        calls = [call(*expected_parameters_1), call(*expected_parameters_2)]
        self.auth.client.execute.assert_has_calls(calls, any_order=True)
