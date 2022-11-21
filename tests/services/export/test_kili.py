# pylint: disable=missing-docstring
from unittest import TestCase

from kili.orm import AnnotationFormat, Asset
from kili.services.export.format.base import BaseExporter
from tests.services.export.fakes.fake_data import (
    kili_format_expected_frame_asset_output,
    kili_format_frame_asset,
)


class KiliTestCase(TestCase):
    def test_process_assets(self):
        clean_assets = BaseExporter.process_assets([Asset(**kili_format_frame_asset)], "raw")
        assert len(clean_assets) == 1
        assert clean_assets[0] == kili_format_expected_frame_asset_output
