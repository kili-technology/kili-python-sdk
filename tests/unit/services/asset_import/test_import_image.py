from unittest.mock import MagicMock, call, patch

import pytest
from requests.exceptions import ReadTimeout

from kili.exceptions import MutationOutcomeUnknownError
from kili.services.asset_import import import_assets
from kili.services.asset_import.exceptions import UploadFromLocalDataForbiddenError
from tests.unit.services.asset_import.base import ImportTestCase
from tests.unit.services.asset_import.mocks import (
    mocked_request_signed_urls,
    mocked_unique_id,
    mocked_upload_data_via_rest,
    organization_generator,
)


@patch("kili.utils.bucket.request_signed_urls", mocked_request_signed_urls)
@patch("kili.utils.bucket.upload_data_via_rest", mocked_upload_data_via_rest)
@patch("kili.utils.bucket.generate_unique_id", mocked_unique_id)
class ImageTestCase(ImportTestCase):
    def test_upload_from_one_local_image(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "IMAGE"}
        url = "https://storage.googleapis.com/label-public-staging/car/car_1.jpg"
        path_image = self.downloader(url)
        assets = [{"content": path_image, "external_id": "local image"}]
        import_assets(self.kili, self.project_id, assets)
        expected_parameters = self.get_expected_sync_call(
            ["https://signed_url?id=id"],
            ["local image"],
            ["unique_id"],
            [False],
            [""],
            ["{}"],
        )
        self.kili.graphql_client.execute.assert_called_with(*expected_parameters)

    def test_upload_from_one_hosted_image(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "IMAGE"}
        assets = [
            {"content": "https://hosted-data", "external_id": "hosted file", "id": "unique_id"}
        ]
        import_assets(self.kili, self.project_id, assets)
        expected_parameters = self.get_expected_sync_call(
            ["https://hosted-data"], ["hosted file"], ["unique_id"], [False], [""], ["{}"]
        )
        self.kili.graphql_client.execute.assert_called_with(*expected_parameters)

    def test_upload_from_one_local_jp2_image(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "IMAGE"}
        url = "https://storage.googleapis.com/label-public-staging/import-testing/test.jp2"
        path_image = self.downloader(url)
        assets = [{"content": path_image, "external_id": "local jp2 image"}]
        import_assets(self.kili, self.project_id, assets)
        expected_parameters = self.get_expected_async_call(
            ["https://signed_url?id=id"],
            ["local jp2 image"],
            ["unique_id"],
            ["{}"],
            "TILED_IMAGE",
        )
        self.kili.graphql_client.execute.assert_called_with(*expected_parameters)

    def test_upload_from_one_local_ntf_image(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "IMAGE"}
        url = "https://storage.googleapis.com/label-public-staging/import-testing/test.ntf"
        path_image = self.downloader(url)
        assets = [{"content": path_image, "external_id": "local ntf image"}]
        import_assets(self.kili, self.project_id, assets)
        expected_parameters = self.get_expected_async_call(
            ["https://signed_url?id=id"],
            ["local ntf image"],
            ["unique_id"],
            ["{}"],
            "TILED_IMAGE",
        )
        self.kili.graphql_client.execute.assert_called_with(*expected_parameters)

    def test_upload_from_one_local_tiff_image(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "IMAGE"}
        url = "https://storage.googleapis.com/label-public-staging/geotiffs/bogota.tif"
        path_image = self.downloader(url)
        assets = [{"content": path_image, "external_id": "local tiff image"}]
        import_assets(self.kili, self.project_id, assets)
        expected_parameters = self.get_expected_async_call(
            ["https://signed_url?id=id"],
            ["local tiff image"],
            ["unique_id"],
            ["{}"],
            "TILED_IMAGE",
        )
        self.kili.graphql_client.execute.assert_called_with(*expected_parameters)

    def test_upload_from_local_tiff_images_for_multi_layer(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "IMAGE"}
        url = "https://storage.googleapis.com/label-public-staging/geotiffs/bogota.tif"
        path_image = self.downloader(url)
        assets = [
            {
                "multi_layer_content": [
                    {"path": path_image, "name": "layer1"},
                    {"path": path_image, "name": "layer2", "isBaseLayer": False},
                ],
                "external_id": "local tiff image",
            }
        ]
        import_assets(self.kili, self.project_id, assets)
        expected_parameters = self.get_expected_async_call_multi_later(
            [
                [
                    {
                        "url": "https://signed_url?id=id",
                        "name": "layer1",
                    },
                    {"url": "https://signed_url?id=id", "name": "layer2", "isBaseLayer": False},
                ]
            ],
            [""],
            ["local tiff image"],
            ["unique_id"],
            ["{}"],
            "TILED_IMAGE",
        )
        self.kili.graphql_client.execute.assert_called_with(*expected_parameters)

    def test_upload_with_one_tiff_and_one_basic_image(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "IMAGE"}
        url_tiff = "https://storage.googleapis.com/label-public-staging/geotiffs/bogota.tif"
        url_basic = "https://storage.googleapis.com/label-public-staging/car/car_1.jpg"
        path_basic = self.downloader(url_basic)
        path_tiff = self.downloader(url_tiff)
        assets = [
            {"content": path_basic, "external_id": "local basic image"},
            {"content": path_tiff, "external_id": "local tiff image"},
        ]
        import_assets(self.kili, self.project_id, assets)
        expected_parameters_sync = self.get_expected_sync_call(
            ["https://signed_url?id=id"],
            ["local basic image"],
            ["unique_id"],
            [False],
            [""],
            ["{}"],
        )
        expected_parameters_async = self.get_expected_async_call(
            ["https://signed_url?id=id"],
            ["local tiff image"],
            ["unique_id"],
            ["{}"],
            "TILED_IMAGE",
        )
        calls = [call(*expected_parameters_sync), call(*expected_parameters_async)]
        self.kili.graphql_client.execute.assert_has_calls(calls, any_order=True)

    def test_upload_from_several_batches(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "IMAGE"}
        self.assert_upload_several_batches()

    def test_upload_splits_batches_by_payload_size(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "IMAGE"}
        ocr = {"fullTextAnnotation": {"text": "x" * 600_000}}  # heavy OCR metadata per asset
        assets = [
            {"content": "https://hosted-data", "external_id": f"ocr {i}", "json_metadata": ocr}
            for i in range(7)
        ]

        def graphql_execute_side_effect(*args, **_):
            nb_asset_batch = len(args[1]["data"]["contentArray"])
            return {"data": [{"id": f"id{i}"} for i in range(nb_asset_batch)]}

        # self.kili is shared by every test: the patch must not outlive this one
        with patch.object(
            self.kili.graphql_client, "execute", side_effect=graphql_execute_side_effect
        ) as execute:
            import_assets(self.kili, self.project_id, assets)

        batches = [c.args[1]["data"]["externalIDArray"] for c in execute.call_args_list]
        # 3 assets of 600 kB fit the initial 2 MB budget, a 4th would not
        assert batches == [["ocr 0", "ocr 1", "ocr 2"], ["ocr 3", "ocr 4", "ocr 5"], ["ocr 6"]]

    def test_upload_from_one_hosted_image_authorized_while_local_forbidden(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "IMAGE"}
        self.kili.kili_api_gateway.list_organizations = MagicMock(
            return_value=organization_generator(upload_local_data=False)
        )
        assets = [
            {"content": "https://hosted-data", "external_id": "hosted file", "id": "unique_id"}
        ]
        import_assets(self.kili, self.project_id, assets)
        expected_parameters = self.get_expected_sync_call(
            ["https://hosted-data"], ["hosted file"], ["unique_id"], [False], [""], ["{}"]
        )
        self.kili.graphql_client.execute.assert_called_with(*expected_parameters)

        url = "https://storage.googleapis.com/label-public-staging/car/car_1.jpg"
        path_image = self.downloader(url)
        assets = [{"content": path_image, "external_id": "local image"}]
        with pytest.raises(UploadFromLocalDataForbiddenError):
            import_assets(self.kili, self.project_id, assets)


@patch("kili.utils.bucket.request_signed_urls", mocked_request_signed_urls)
@patch("kili.utils.bucket.upload_data_via_rest", mocked_upload_data_via_rest)
@patch("kili.utils.bucket.generate_unique_id", mocked_unique_id)
class AsyncUploadTypeTestCase(ImportTestCase):
    """Tests which uploadType the async import sends.

    `GEOSPATIAL` keeps `GEO_SATELLITE`; every other async import is a tiled image.
    """

    def test_upload_to_geospatial_project_still_uses_geo_satellite(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "GEOSPATIAL"}
        url = "https://storage.googleapis.com/label-public-staging/geotiffs/bogota.tif"
        path_image = self.downloader(url)
        assets = [{"content": path_image, "external_id": "local tiff image"}]
        import_assets(self.kili, self.project_id, assets)
        expected_parameters = self.get_expected_async_call(
            ["https://signed_url?id=id"],
            ["local tiff image"],
            ["unique_id"],
            ["{}"],
            "GEO_SATELLITE",
        )
        self.kili.graphql_client.execute.assert_called_with(*expected_parameters)


@patch("kili.utils.bucket.request_signed_urls", mocked_request_signed_urls)
@patch("kili.utils.bucket.upload_data_via_rest", mocked_upload_data_via_rest)
@patch("kili.utils.bucket.generate_unique_id", mocked_unique_id)
class UnknownOutcomeTestCase(ImportTestCase):
    def test_a_batch_with_an_unknown_outcome_is_named_by_its_external_ids(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "IMAGE"}
        assets = [
            {"content": "https://hosted-data", "external_id": f"asset {i}"} for i in range(150)
        ]
        unknown = MutationOutcomeUnknownError("appendManyAssets", ReadTimeout())

        def graphql_execute_side_effect(*args, **_):
            external_ids = args[1]["data"]["externalIDArray"]
            if external_ids[0] == "asset 100":
                raise unknown
            return {"data": [{"id": f"id{i}"} for i in range(len(external_ids))]}

        with patch.object(
            self.kili.graphql_client, "execute", side_effect=graphql_execute_side_effect
        ), pytest.raises(MutationOutcomeUnknownError, match="asset 100, asset 101") as raised:
            import_assets(self.kili, self.project_id, assets)

        assert raised.value.external_ids == [f"asset {i}" for i in range(100, 150)]
        assert raised.value.index is None  # a position would not locate it once assets are filtered

    def test_a_batch_without_external_ids_is_named_by_the_ids_it_was_sent_with(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "IMAGE"}
        assets = [{"content": "https://hosted-data"} for _ in range(150)]
        unknown = MutationOutcomeUnknownError("appendManyAssets", ReadTimeout())
        sent: list[list[str]] = []

        def graphql_execute_side_effect(*args, **_):
            sent.append(args[1]["data"]["externalIDArray"])
            if len(sent) == 2:
                raise unknown
            return {"data": [{"id": f"id{i}"} for i in range(len(sent[-1]))]}

        with patch.object(
            self.kili.graphql_client, "execute", side_effect=graphql_execute_side_effect
        ), pytest.raises(MutationOutcomeUnknownError) as raised:
            import_assets(self.kili, self.project_id, assets)

        assert raised.value.external_ids == sent[1]  # the generated ids, as the server got them
        assert "None" not in raised.value.external_ids
