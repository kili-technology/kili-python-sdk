# pylint: disable=missing-function-docstring,redefined-outer-name
"""
Tests that the external id check is strict
"""
import json
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest
import requests

from kili.client import Kili


@pytest.fixture()
def text():
    return "Youʼll see Johnʼs car"


@pytest.fixture
def kili():
    return Kili()


@pytest.fixture()
def project_with_assets(kili, text):
    interface = {
        "jobs": {
            "JOB_0": {
                "mlTask": "CLASSIFICATION",
                "required": 1,
                "content": {
                    "categories": {
                        "OBJECT_A": {"name": "Object A", "id": "A"},
                        "OBJECT_B": {"name": "Object B", "id": "B"},
                    },
                    "input": "radio",
                },
            }
        }
    }

    project = kili.create_project(
        input_type="TEXT",
        json_interface=interface,
        title="Test for ML-782",
        description="Test for ML-782",
    )

    kili.append_many_to_dataset(
        project_id=project["id"],
        content_array=[text],
        external_id_array=["apostroph_1"],
        disable_tqdm=True,
    )

    yield project

    kili.delete_many_from_dataset(list(a["id"] for a in kili.assets(project["id"], fields=["id"])))
    kili.delete_project(project["id"])


def test_encoding_decoding_consistency(text, kili, project_with_assets):
    """
    Test query by external id
    """

    retrieved_assets = list(
        kili.assets(
            project_with_assets["id"],
            external_id_contains=["apostroph_1"],
            fields=["content"],
            disable_tqdm=True,
        )
    )

    assert requests.get(retrieved_assets[0]["content"], timeout=30).text == text
