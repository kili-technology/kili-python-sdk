import json
from unittest.mock import MagicMock

from kili.services.asset_import.base import BaseBatchImporter, BatchParams


def test_metadata_is_sized_as_the_string_it_is_sent_as():
    importer = BaseBatchImporter(
        MagicMock(), MagicMock(), BatchParams(is_hosted=True, is_asynchronous=False), MagicMock()
    )
    metadata = {"fullTextAnnotation": {"text": 'a "quoted" word ' * 1000}}

    size = importer.payload_size({"external_id": "ocr", "json_metadata": metadata})

    sent = {"external_id": "ocr", "json_metadata": json.dumps(metadata)}
    assert size == len(json.dumps(sent))
