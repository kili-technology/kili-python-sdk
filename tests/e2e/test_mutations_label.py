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
        title="test_mutations_label",
        description="test_mutations_label",
    )

    kili.append_many_to_dataset(
        project_id=project["id"], content_array=["some text"], external_id_array=["1"]
    )

    for _ in range(4):
        kili.append_labels(
            project_id=project["id"],
            asset_external_id_array=["1"],
            json_response_array=[{"CLASSIFICATION_JOB": {"categories": ["A"]}}],
        )

    assert kili.count_labels(project_id=project["id"]) == 4

    yield project

    kili.delete_project(project["id"])


def test_delete_labels(kili: Kili, project: Dict):
    # Given
    labels = kili.labels(project_id=project["id"], fields=["id"])
    label_ids = [label["id"] for label in labels]
    assert len(label_ids) == 4

    # When
    labels_to_delete_ids, labels_to_keep = label_ids[:2], label_ids[2:]
    kili.delete_labels(ids=labels_to_delete_ids)

    # Then
    labels_left = kili.labels(project_id=project["id"], fields=["id"])
    labels_left_ids = [label["id"] for label in labels_left]
    assert sorted(labels_left_ids) == sorted(labels_to_keep)
