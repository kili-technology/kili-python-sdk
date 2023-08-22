from pathlib import Path

import pytest

from kili.entrypoints.queries.label import QueriesLabel
from kili.services.export.exceptions import NotCompatibleOptions
from kili.services.export.format.voc import _convert_from_kili_to_voc_format
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
    }
    mocker.patch("kili.services.export.get_project", return_value=get_project_return_val)
    mocker.patch(
        "kili.entrypoints.queries.asset.media_downloader.ProjectQuery.__call__",
        return_value=(i for i in [get_project_return_val]),
    )
    mocker.patch(
        "kili.services.export.format.base.get_project", return_value=get_project_return_val
    )
    mocker.patch(
        "kili.services.export.format.base.DataConnectionsQuery.__call__",
        return_value=(i for i in [{"id": "fake_data_connection_id"}]),
    )

    kili = QueriesLabel()
    kili.api_endpoint = "https://"  # type: ignore
    kili.api_key = ""  # type: ignore
    kili.graphql_client = mocker.MagicMock()
    kili.http_client = mocker.MagicMock()

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
