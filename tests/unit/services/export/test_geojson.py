import json
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import pytest_mock

from kili.entrypoints.queries.label import QueriesLabel
from kili.orm import Asset


def test_kili_export_labels_geojson(mocker: pytest_mock.MockerFixture):
    get_project_return_val = {
        "jsonInterface": {"jobs": {"JOB": {"tools": ["rectangle"], "mlTask": "OBJECT_DETECTION"}}},
        "inputType": "IMAGE",
        "title": "fake proj title",
        "id": "fake_proj_id",
        "description": "fake proj description",
    }
    mocker.patch("kili.services.export.get_project", return_value=get_project_return_val)
    # mocker.patch(
    #     "kili.entrypoints.queries.asset.media_downloader.ProjectQuery.__call__",
    #     return_value=(i for i in [get_project_return_val]),
    # )
    mocker.patch(
        "kili.services.export.format.base.get_project", return_value=get_project_return_val
    )
    mocker.patch(
        "kili.services.export.format.base.DataConnectionsQuery.__call__",
        return_value=(i for i in [{"id": "fake_data_connection_id"}]),
    )
    mocker.patch(
        "kili.services.export.format.base.fetch_assets",
        return_value=[
            Asset(asset)
            for asset in json.load(
                open("./tests/unit/services/export/fakes/geotiff_image_project_assets.json")
            )
        ],
    )

    kili = QueriesLabel()
    kili.api_endpoint = "https://"  # type: ignore
    kili.api_key = ""  # type: ignore
    kili.graphql_client = mocker.MagicMock()
    kili.http_client = mocker.MagicMock()
    kili.kili_api_gateway = mocker.MagicMock()
    kili.kili_api_gateway.get_project.return_value = {"inputType": "IMAGE"}

    kili.export_labels(
        "fake_proj_id",
        filename="export_geojson.zip",
        fmt="geojson",
        with_assets=False,
        layout="merged",
    )

    with TemporaryDirectory() as extract_folder:
        with ZipFile("export_geojson.zip", "r") as z_f:
            # extract in a temp dir
            z_f.extractall(extract_folder)

        assert Path(f"{extract_folder}/README.kili.txt").is_file()
        assert Path(f"{extract_folder}/labels").is_dir()
        assert Path(f"{extract_folder}/labels/sample.geojson").is_file()

        with Path(f"{extract_folder}/labels/sample.geojson").open() as f:
            output = json.load(f)

    assert output["type"] == "FeatureCollection"
    assert len(output["features"]) == 5  # 5 annotations in geotiff_image_project_assets.json
