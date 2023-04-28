# pylint: disable=missing-function-docstring,redefined-outer-name
"""Tests that the external id check is strict."""
import pytest

from kili.client import Kili


@pytest.fixture
def kili():
    return Kili()


@pytest.fixture()
def project_with_assets(kili):
    interface = {
        "jobs": {
            "JOB_0": {
                "mlTask": "CLASSIFICATION",
                "required": 1,
                "content": {
                    "categories": {
                        "OBJECT_A": {"name": "Object A"},
                        "OBJECT_B": {"name": "Object B"},
                    },
                    "input": "radio",
                },
            }
        }
    }

    project = kili.create_project(
        input_type="TEXT",
        json_interface=interface,
        title="Test for ML-755",
        description="Test for ML-755",
    )

    kili.append_many_to_dataset(
        project_id=project["id"],
        content_array=["Hello there", "This is some text", "I would like to retrieve"],
        external_id_array=["text_1_", "text_10_", "text_11_"],
        disable_tqdm=True,
    )

    yield project

    kili.delete_many_from_dataset(list(a["id"] for a in kili.assets(project["id"], fields=["id"])))
    kili.delete_project(project["id"])


def test_query_asset_by_external_id(kili, project_with_assets):
    """Test query by external id."""
    retrieved_assets = kili.assets(
        project_with_assets["id"], external_id_strictly_in=["text_1_"], fields=["externalId"]
    )

    assert len(retrieved_assets) == 1
    assert retrieved_assets[0]["externalId"] == "text_1_"


def test_query_asset_by_external_id_not_strictly_in(kili, project_with_assets):
    """Test query by external id."""
    retrieved_assets = kili.assets(
        project_with_assets["id"], external_id_in=["text_1"], fields=["externalId"]
    )

    assert len(retrieved_assets) == 3
    assert sorted([a["externalId"] for a in retrieved_assets]) == sorted(
        ["text_1_", "text_10_", "text_11_"]
    )
