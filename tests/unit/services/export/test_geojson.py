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
    kili.kili_api_gateway.get_current_user.return_value = {"email": "exporter@kili-technology.com"}

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


def test_geospatial_project_export_fetches_and_attaches_metadata(
    mocker: pytest_mock.MockerFixture,
):
    """For GEOSPATIAL projects the metadata field is fetched and injected into the output."""
    geospatial_export_metadata = [{"layerName": "RGB", "crs": "EPSG:32634"}]
    get_project_return_val = {
        "jsonInterface": {"jobs": {"JOB": {"tools": ["rectangle"], "mlTask": "OBJECT_DETECTION"}}},
        "inputType": "GEOSPATIAL",
        "title": "fake proj title",
        "id": "fake_proj_id",
        "description": "fake proj description",
    }
    mocker.patch.object(GeoJsonExporter, "_has_data_connection", return_value=False)
    fetch_assets_mock = mocker.patch(
        "kili.services.export.format.base.fetch_assets",
        return_value=[
            {
                "id": "asset_id_1",
                "externalId": "sample",
                "geospatialExportMetadata": geospatial_export_metadata,
                "latestLabel": {
                    "author": {"email": "jane@kili-technology.com"},
                    "jsonResponse": {
                        "JOB": {
                            "annotations": [
                                {
                                    "categories": [{"name": "A"}],
                                    "mid": "mid_1",
                                    "type": "rectangle",
                                    "boundingPoly": [
                                        {
                                            "normalizedVertices": [
                                                {"x": 0.1, "y": 0.1},
                                                {"x": 0.1, "y": 0.2},
                                                {"x": 0.2, "y": 0.2},
                                                {"x": 0.2, "y": 0.1},
                                            ]
                                        }
                                    ],
                                    "children": {},
                                }
                            ]
                        }
                    },
                },
            }
        ],
    )

    kili = LabelClientMethods()
    kili.api_endpoint = "https://"  # type: ignore
    kili.api_key = ""  # type: ignore
    kili.graphql_client = mocker.MagicMock()  # pyright: ignore[reportGeneralTypeIssues]
    kili.http_client = mocker.MagicMock()  # pyright: ignore[reportGeneralTypeIssues]
    kili.kili_api_gateway = mocker.MagicMock()
    kili.kili_api_gateway.get_project.return_value = get_project_return_val
    kili.kili_api_gateway.get_current_user.return_value = {"email": "exporter@kili-technology.com"}

    with TemporaryDirectory() as export_folder:
        export_filename = str(Path(export_folder) / "export_geojson.zip")

        kili.export_labels(
            "fake_proj_id",
            filename=export_filename,
            fmt="geojson",
            with_assets=False,
            layout="merged",
        )

        # The metadata field is requested only for GEOSPATIAL projects.
        assert fetch_assets_mock.call_args.kwargs["additional_fields"] == [
            "geospatialExportMetadata"
        ]

        with TemporaryDirectory() as extract_folder:
            with ZipFile(export_filename, "r") as z_f:
                z_f.extractall(extract_folder)

            with Path(f"{extract_folder}/labels/sample.geojson").open() as f:
                output = json.load(f)

    assert output["type"] == "FeatureCollection"
    assert output["features"]
    # Asset/export-level metadata sits once at the root under properties.kili.
    root_kili = output["properties"]["kili"]
    assert root_kili["geospatialExportMetadata"] == geospatial_export_metadata
    assert root_kili["assetId"] == "asset_id_1"
    assert root_kili["author"] == "jane@kili-technology.com"
    assert root_kili["exportDate"]  # ISO-8601 timestamp generated at export time
    for feature in output["features"]:
        assert "geospatialExportMetadata" not in feature["properties"]["kili"]
        assert "assetId" not in feature["properties"]["kili"]


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


def test_process_asset_with_latest_labels(tmp_path: Path):
    """Test that multiple labels create separate GeoJSON files with label suffix."""
    asset = {
        "latestLabels": [
            {
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
            {
                "jsonResponse": {
                    "JOB_0": {
                        "annotations": [
                            {
                                "categories": [{"name": "OBJECT_B"}],
                                "mid": "20230111125258113-44529",
                                "type": "rectangle",
                                "boundingPoly": [
                                    {
                                        "normalizedVertices": [
                                            {"x": 0.1, "y": 0.2},
                                            {"x": 0.1, "y": 0.1},
                                            {"x": 0.2, "y": 0.1},
                                            {"x": 0.2, "y": 0.2},
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
        ],
        "externalId": "multi_label",
    }
    label_path = Path(tmp_path) / "labels"
    _process_asset(asset, label_path)

    # Should create two GeoJSON files with label suffixes
    assert Path(label_path / "multi_label_label1.geojson").is_file()
    assert Path(label_path / "multi_label_label2.geojson").is_file()


def test_process_asset_attaches_export_metadata_to_properties_kili(tmp_path: Path):
    """AssetId, author, exportDate and geospatial metadata land in properties.kili."""
    geospatial_export_metadata = [
        {"layerName": "RGB", "crs": "EPSG:32634"},
        {"layerName": "DSM", "crs": "EPSG:4326"},
    ]
    asset = {
        "id": "asset_id_1",
        "latestLabel": {
            "author": {"email": "jane@kili-technology.com"},
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
                                        {"x": 0.61, "y": 0.76},
                                        {"x": 0.61, "y": 0.39},
                                        {"x": 0.89, "y": 0.39},
                                        {"x": 0.89, "y": 0.76},
                                    ]
                                }
                            ],
                            "children": {},
                        }
                    ]
                }
            },
        },
        "externalId": "geospatial_asset",
        "geospatialExportMetadata": geospatial_export_metadata,
    }
    label_path = Path(tmp_path) / "labels"

    _process_asset(
        asset,
        label_path,
        flatten_properties=True,
        export_date="2026-07-21T10:00:00.000Z",
    )

    with (label_path / "geospatial_asset.geojson").open() as file:
        output = json.load(file)

    assert "geospatialExportMetadata" not in output
    assert output["features"]
    # Asset/export-level metadata sits once at the root under properties.kili.
    root_kili = output["properties"]["kili"]
    assert root_kili["geospatialExportMetadata"] == geospatial_export_metadata
    assert root_kili["assetId"] == "asset_id_1"
    # `author` is taken from the label's author, not the export requester.
    assert root_kili["author"] == "jane@kili-technology.com"
    assert root_kili["exportDate"] == "2026-07-21T10:00:00.000Z"
    for feature in output["features"]:
        assert "geospatialExportMetadata" not in feature["properties"]["kili"]
        assert "assetId" not in feature["properties"]["kili"]
