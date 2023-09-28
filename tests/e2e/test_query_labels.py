from typing import Dict

import pytest

from kili.client import Kili


@pytest.fixture(scope="module")
def project_id(kili: Kili):
    project = kili.create_project(
        "TEXT",
        json_interface={
            "jobs": {
                "CLASSIFICATION_JOB": {
                    "content": {
                        "categories": {"A": {"children": [], "name": "A"}},
                        "input": "radio",
                    },
                    "instruction": "Classif",
                    "mlTask": "CLASSIFICATION",
                    "required": 1,
                    "isChild": False,
                }
            }
        },
        title="test e2e query labels sdk",
    )

    kili.append_many_to_dataset(
        project_id=project["id"],
        content_array=["text asset 1", "text asset 2"],
        external_id_array=["asset_1", "asset_2"],
    )

    kili.append_labels(
        project_id=project["id"],
        asset_external_id_array=["asset_1", "asset_2"],
        json_response_array=[{"CLASSIFICATION_JOB": {"categories": [{"name": "A"}]}}] * 2,
    )

    yield project["id"]

    kili.delete_project(project["id"])


@pytest.mark.parametrize(
    ("labels_query_params", "nb_expected_labels"),
    [
        ({"asset_external_id_in": ["asset_"]}, 2),
        ({"asset_external_id_in": ["asset_1"]}, 1),
        ({"asset_external_id_strictly_in": ["asset_1"]}, 1),
        ({"asset_external_id_strictly_in": ["asset_"]}, 0),
    ],
)
def test_given_project_with_labels_when_i_query_with_filters_then_it_works(
    project_id: str, kili: Kili, labels_query_params: Dict, nb_expected_labels: int
):
    # Given
    _ = project_id

    # When
    labels = kili.labels(
        project_id=project_id,
        fields=("labelOf.externalId",),
        **labels_query_params,
    )

    # Then
    assert len(labels) == nb_expected_labels
