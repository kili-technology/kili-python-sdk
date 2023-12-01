import json
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import pytest_mock

from kili.presentation.client.label import LabelClientMethods
from kili.services.export.format.geojson import GeoJsonExporter, _process_asset


def test_kili_export_labels_geojson(mocker: pytest_mock.MockerFixture):
    # Given
    get_project_return_val = {
        "jsonInterface": {"jobs": {"JOB": {"tools": ["rectangle"], "mlTask": "OBJECT_DETECTION"}}},
        "inputType": "IMAGE",
        "title": "fake proj title",
        "id": "fake_proj_id",
        "description": "fake proj description",
    }
    mocker.patch.object(GeoJsonExporter, "_has_data_connection", return_value=False)
    mocker.patch(
        "kili.services.export.format.base.fetch_assets",
        return_value=[
            asset
            for asset in json.load(
                open("./tests/unit/services/export/fakes/geotiff_image_project_assets.json")
            )
        ],
    )

    kili = LabelClientMethods()
    kili.api_endpoint = "https://"  # type: ignore
    kili.api_key = ""  # type: ignore
    kili.graphql_client = mocker.MagicMock()  # pyright: ignore[reportGeneralTypeIssues]
    kili.http_client = mocker.MagicMock()  # pyright: ignore[reportGeneralTypeIssues]
    kili.kili_api_gateway = mocker.MagicMock()
    kili.kili_api_gateway.get_project.return_value = get_project_return_val

    with TemporaryDirectory() as export_folder:
        export_filename = str(Path(export_folder) / "export_geojson.zip")

        # When
        kili.export_labels(
            "fake_proj_id",
            filename=export_filename,
            fmt="geojson",
            with_assets=False,
            layout="merged",
        )

        with TemporaryDirectory() as extract_folder:
            with ZipFile(export_filename, "r") as z_f:
                # extract in a temp dir
                z_f.extractall(extract_folder)

            # Then
            assert Path(f"{extract_folder}/README.kili.txt").is_file()
            assert Path(f"{extract_folder}/labels").is_dir()
            assert Path(f"{extract_folder}/labels/sample.geojson").is_file()

            with Path(f"{extract_folder}/labels/sample.geojson").open() as f:
                output = json.load(f)

    assert output["type"] == "FeatureCollection"
    assert len(output["features"]) == 5  # 5 annotations in geotiff_image_project_assets.json


def test_process_asset_with_external_id_containing_slash(tmp_path: Path):
    asset = {
        "latestLabel": {
            "jsonResponse": {
                "JOB_0": {
                    "annotations": [
                        {
                            "categories": [{"name": "OBJECT_A"}],
                            "mid": "20230111125258113-44528",
                            "type": "rectangle",
                            "boundingPoly": [
                                {
                                    "normalizedVertices": [
                                        {"x": 0.6101435505380516, "y": 0.7689773770786136},
                                        {"x": 0.6101435505380516, "y": 0.39426226491370664},
                                        {"x": 0.8962087421313937, "y": 0.39426226491370664},
                                        {"x": 0.8962087421313937, "y": 0.7689773770786136},
                                    ]
                                }
                            ],
                            "polyline": [],
                            "children": {},
                        }
                    ]
                }
            }
        },
        "externalId": "a/b.png",
    }
    label_path = Path(tmp_path) / "labels"
    _process_asset(asset, label_path)

    assert Path(label_path / "a/b.png.geojson").is_file()
