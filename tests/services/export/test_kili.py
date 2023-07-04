import pytest_mock

from kili.orm import Asset
from kili.services.export.format.base import AbstractExporter
from tests.fakes.fake_data import (
    kili_format_expected_frame_asset_output,
    kili_format_frame_asset,
)


def test_preprocess_assets(mocker: pytest_mock.MockFixture):
    mocker_exporter = mocker.MagicMock()
    clean_assets = AbstractExporter.preprocess_assets(
        mocker_exporter, [Asset(**kili_format_frame_asset)], "raw"
    )
    assert len(clean_assets) == 1
    assert clean_assets[0] == kili_format_expected_frame_asset_output
