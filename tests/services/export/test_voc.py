import os
from pathlib import Path
from unittest import TestCase

from kili.services.export.format.voc import _convert_from_kili_to_voc_format
from kili.utils.tempfile import TemporaryDirectory
from tests.services.export.fakes.fake_content_repository import FakeContentRepository
from tests.services.export.fakes.fake_data import (
    asset_image_1,
    asset_video,
    category_ids,
)


def test__convert_from_kili_to_voc_format():
    parameters = {"filename": f'{asset_image_1["externalId"]}.xml'}
    annotations = _convert_from_kili_to_voc_format(
        response=asset_image_1["latestLabel"]["jsonResponse"],
        img_width=1920,
        img_height=1080,
        parameters=parameters,
    )
    expected_annotations = Path("./tests/services/export/expected/car_1.xml").read_text(
        encoding="utf-8"
    )
    assert annotations == expected_annotations
