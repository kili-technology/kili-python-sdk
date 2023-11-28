from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from kili.presentation.client.label import LabelClientMethods
from kili.services.export import VocExporter
from kili.services.export.exceptions import NotCompatibleOptions
from kili.services.export.format.voc import _convert_from_kili_to_voc_format, _process_asset
from tests.fakes.fake_data import asset_image_1, asset_image_1_without_annotation


def test__convert_from_kili_to_voc_format():
    parameters = {"filename": f'{asset_image_1["externalId"]}.xml'}
    annotations = _convert_from_kili_to_voc_format(
        response=asset_image_1["latestLabel"]["jsonResponse"],
        img_width=1920,
        img_height=1080,
        parameters=parameters,
        valid_jobs=["JOB_0"],
    )
    expected_annotations = Path("./tests/unit/services/export/expected/car_1.xml").read_text(
        encoding="utf-8"
    )
    assert annotations == expected_annotations


def test__convert_from_kili_to_voc_format_no_annotation():
    parameters = {"filename": f'{asset_image_1["externalId"]}.xml'}
    annotations = _convert_from_kili_to_voc_format(
        response=asset_image_1_without_annotation,
        img_width=1920,
        img_height=1080,
        parameters=parameters,
        valid_jobs=["JOB_0"],
    )
    expected_annotations = Path(
        "./tests/unit/services/export/expected/car_1_without_annotation.xml"
    ).read_text(encoding="utf-8")
    assert annotations == expected_annotations


def test_when_exporting_to_voc_given_a_project_with_data_connection_then_it_should_crash(mocker):
    get_project_return_val = {
        "jsonInterface": {"jobs": {"JOB": {"tools": ["rectangle"], "mlTask": "OBJECT_DETECTION"}}},
        "inputType": "IMAGE",
        "title": "",
        "id": "fake_proj_id",
        "dataConnections": None,
    }
    mocker.patch.object(VocExporter, "_has_data_connection", return_value=True)

    kili = LabelClientMethods()
    kili.api_endpoint = "https://"  # type: ignore
    kili.api_key = ""  # type: ignore
    kili.graphql_client = mocker.MagicMock()  # pyright: ignore[reportGeneralTypeIssues]
    kili.http_client = mocker.MagicMock()  # pyright: ignore[reportGeneralTypeIssues]
    kili.kili_api_gateway = mocker.MagicMock()
    kili.kili_api_gateway.get_project.return_value = get_project_return_val

    with pytest.raises(
        NotCompatibleOptions,
        match="Export with download of assets is not allowed on projects with data connections.",
    ):
        kili.export_labels(
            project_id="fake_proj_id",
            filename="fake_filename",
            fmt="pascal_voc",
            layout="merged",
            with_assets=True,
        )


def test_process_asset_image_with_external_id():
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
        "resolution": {"width": 1920, "height": 1080},
        "content": "fakecontent",
    }
    with TemporaryDirectory() as f:
        label_path = Path(f) / "labels"
        _process_asset(asset, label_path, "IMAGE", ["JOB_0"])
        assert Path(label_path / "a/b.png.xml").is_file()
