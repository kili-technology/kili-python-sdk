import json
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import pytest_mock

from kili.presentation.client.label import LabelClientMethods
from kili.services.export.format.geojson import GeoJsonExporter


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
