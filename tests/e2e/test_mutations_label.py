from typing import Dict

import pytest

from kili.client import Kili


@pytest.fixture
def kili() -> Kili:
    return Kili()


@pytest.fixture
def project(kili: Kili):
    interface = {
        "jobs": {
            "CLASSIFICATION_JOB": {
                "content": {"categories": {"A": {"children": [], "name": "A"}}, "input": "radio"},
                "instruction": "classif",
                "mlTask": "CLASSIFICATION",
                "required": 1,
                "isChild": False,
            }
        }
    }

    project = kili.create_project(
        input_type="TEXT",
        json_interface=interface,
        title="test_e2e_delete_labels",
        description="test_e2e_delete_labels",
    )

    kili.append_many_to_dataset(
        project_id=project["id"],
        content_array=["asset_content_1", "asset_content_2"],
        external_id_array=["1", "2"],
    )

    kili.append_labels(
        project_id=project["id"],
        asset_external_id_array=["1", "2"] * 2,
        json_response_array=[{"CLASSIFICATION_JOB": {"categories": ["A"]}}] * 4,
        label_type="PREDICTION",
        model_name="model_name",
    )

    assert kili.count_labels(project_id=project["id"]) == 4

    yield project

    kili.delete_project(project["id"])


@pytest.mark.skip(reason="not available on staging yet")
def test_e2e_delete_labels(kili: Kili, project: Dict):
    # Given
    labels = kili.labels(project_id=project["id"], fields=["id"])
    label_ids = [label["id"] for label in labels]
    assert len(label_ids) == 4

    # When
    labels_to_delete_ids, labels_to_keep = label_ids[:2], label_ids[2:]
    deleted_label_ids = kili.delete_labels(ids=labels_to_delete_ids)

    # Then
    assert sorted(deleted_label_ids) == sorted(labels_to_delete_ids)

    labels_left_in_project = kili.labels(project_id=project["id"], fields=["id"])
    labels_left_in_project_ids = [label["id"] for label in labels_left_in_project]
    assert sorted(labels_left_in_project_ids) == sorted(labels_to_keep)


@pytest.mark.skip(reason="not available on staging yet")
def test_e2e_append_labels_overwrite(kili: Kili, project: Dict):
    # Given
    labels = kili.labels(project_id=project["id"], fields=["id", "labelOf.externalId"])
    label_ids = [label["id"] for label in labels]
    assert len(label_ids) == 4

    # When
    json_response = {"CLASSIFICATION_JOB": {"categories": ["A"]}}
    kili.append_labels(
        project_id=project["id"],
        json_response_array=[json_response],
        model_name="model_name",
        asset_external_id_array=["1"],
        overwrite=True,
    )

    # Then
    new_labels = kili.labels(project_id=project["id"], fields=["id"])
    new_label_ids = [label["id"] for label in new_labels]
    assert len(new_labels) == 3

    old_pred_ids_asset_1 = [
        label["id"] for label in labels if label["labelOf"]["externalId"] == "1"
    ]
    for label_id in old_pred_ids_asset_1:
        assert label_id not in new_label_ids
