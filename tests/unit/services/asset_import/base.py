import shutil
import tempfile
from unittest import TestCase
from unittest.mock import MagicMock, call

import requests

from kili.adapters.http_client import HttpClient
from kili.core.graphql.operations.asset.mutations import (
    GQL_APPEND_MANY_ASSETS,
    GQL_APPEND_MANY_FRAMES_TO_DATASET,
)
from kili.services.asset_import import import_assets
from kili.services.asset_import.constants import IMPORT_BATCH_SIZE
from tests.unit.services.asset_import.mocks import mocked_auth

from .helpers import LocalDownloader


class ImportTestCase(TestCase):
    def setUp(self):
        self.project_id = "project_id"
        self.test_dir = tempfile.mkdtemp()
        self.downloader = LocalDownloader(
            self.test_dir,
            HttpClient(
                kili_endpoint="https://fake_endpoint.kili-technology.com", api_key="", verify=True
            ),
        )
        self.kili = mocked_auth
        self.kili.kili_api_gateway.count_assets = MagicMock(return_value=1)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def get_expected_sync_call(
        self,
        content_array,
        external_id_array,
        id_array,
        is_honeypot_array,
        json_content_array,
        json_metadata_array,
    ):
        return (
            GQL_APPEND_MANY_ASSETS,
            {
                "data": {
                    "contentArray": content_array,
                    "externalIDArray": external_id_array,
                    "idArray": id_array,
                    "isHoneypotArray": is_honeypot_array,
                    "jsonContentArray": json_content_array,
                    "jsonMetadataArray": json_metadata_array,
                },
                "where": {"id": self.project_id},
            },
        )

    def get_expected_async_call(
        self, content_array, external_id_array, id_array, json_metadata_array, upload_type
    ):
        return (
            GQL_APPEND_MANY_FRAMES_TO_DATASET,
            {
                "data": {
                    "contentArray": content_array,
                    "idArray": id_array,
                    "externalIDArray": external_id_array,
                    "jsonMetadataArray": json_metadata_array,
                    "uploadType": upload_type,
                },
                "where": {"id": self.project_id},
            },
        )

    def assert_upload_several_batches(self):
        nb_asset_test = IMPORT_BATCH_SIZE + 5
        external_id_array = [f"hosted file {i}" for i in range(nb_asset_test)]
        assets = [
            {"content": "https://hosted-data", "external_id": external_id}
            for external_id in external_id_array
        ]

        def graphql_execute_side_effect(*args, **kwargs):
            if args[0] == GQL_APPEND_MANY_ASSETS:
                nb_asset_batch = len(args[1]["data"]["contentArray"])
                return {"data": [{"id": f"id{str(i)}"} for i in range(nb_asset_batch)]}
            else:
                return MagicMock()

        self.kili.graphql_client.execute = MagicMock(side_effect=graphql_execute_side_effect)
        created_assets = import_assets(self.kili, self.project_id, assets)
        expected_parameters_1 = self.get_expected_sync_call(
            ["https://hosted-data"] * IMPORT_BATCH_SIZE,
            [external_id_array[i] for i in range(IMPORT_BATCH_SIZE)],
            ["unique_id"] * IMPORT_BATCH_SIZE,
            [False] * IMPORT_BATCH_SIZE,
            [""] * IMPORT_BATCH_SIZE,
            ["{}"] * IMPORT_BATCH_SIZE,
        )
        expected_parameters_2 = self.get_expected_sync_call(
            ["https://hosted-data"] * 5,
            [external_id_array[i] for i in range(IMPORT_BATCH_SIZE, IMPORT_BATCH_SIZE + 5)],
            ["unique_id"] * 5,
            [False] * 5,
            [""] * 5,
            ["{}"] * 5,
        )
        calls = [call(*expected_parameters_1), call(*expected_parameters_2)]
        self.kili.graphql_client.execute.assert_has_calls(calls, any_order=True)
        assert len(created_assets) == nb_asset_test
