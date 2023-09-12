import pytest

from kili.client import Kili


@pytest.fixture()
def project_id(kili: Kili):
    json_interface = {
        "jobs": {
            "JOB_0": {
                "content": {
                    "categories": {
                        "OBJECT_A": {
                            "children": [],
                            "name": "Object A",
                            "color": "#733AFB",
                            "points": [],
                            "id": "category1",
                        },
                        "OBJECT_B": {
                            "children": [],
                            "name": "Object B",
                            "color": "#3CD876",
                            "points": [],
                            "id": "category2",
                        },
                    },
                    "input": "radio",
                },
                "instruction": "Categories",
                "isChild": False,
                "tools": ["polygon"],
                "mlTask": "OBJECT_DETECTION",
                "models": {},
                "isVisible": True,
                "required": 1,
            },
            "CLASSIFICATION_JOB": {
                "content": {
                    "categories": {
                        "CAS_1": {"children": [], "name": "cas 1", "points": [], "id": "category3"},
                        "CAS_2": {"name": "cas 2", "children": [], "points": [], "id": "category4"},
                        "CAS_3": {"name": "cas 3", "children": [], "points": [], "id": "category5"},
                    },
                    "input": "radio",
                },
                "instruction": "tets",
                "mlTask": "CLASSIFICATION",
                "required": 1,
                "isChild": False,
            },
        }
    }

    project = kili.create_project(
        input_type="IMAGE", json_interface=json_interface, title="Example"
    )
    project_id = project["id"]

    yield project_id

    kili.delete_project(project_id)


def test_paginated_calls_project(kili: Kili, project_id: str):
    # Given assets to import
    url = "https://storage.googleapis.com/label-public-staging/car/car_1.jpg"
    nb_assets = 600

    # When importing
    result = kili.append_many_to_dataset(
        project_id=project_id,
        content_array=[url for i in range(nb_assets)],
        external_id_array=[str(i) for i in range(nb_assets)],
        json_content_array=None,
    )

    # Then count is right
    assert result
    assert result["id"] == project_id
    assert len(result["asset_ids"]) == nb_assets
    assert kili.count_assets(project_id=project_id) == nb_assets

    # When updating asset external_ids
    new_external_ids = [f"modified_name_{i}" for i in range(nb_assets)]
    asset_ids = [asset["id"] for asset in kili.assets(project_id=project_id, fields=["id"])]
    result = kili.change_asset_external_ids(asset_ids=asset_ids, new_external_ids=new_external_ids)

    # Then
    assert len(result) == nb_assets
    new_assets_external_ids = [
        asset["externalId"] for asset in kili.assets(project_id=project_id, fields=("externalId",))
    ]
    assert "modified_name" in new_assets_external_ids[0]
    assert "modified_name" in new_assets_external_ids[550]

    # When creating predictions from paginated calls
    json_response = {
        "JOB_0": {
            "annotations": [
                {
                    "boundingPoly": [
                        {
                            "normalizedVertices": [
                                {"x": 0.16, "y": 0.82},
                                {"x": 0.16, "y": 0.32},
                                {"x": 0.82, "y": 0.32},
                                {"x": 0.82, "y": 0.82},
                            ]
                        }
                    ],
                    "categories": [{"name": "OBJECT_A", "confidence": 100}],
                    "mid": "unique-tesla",
                    "type": "polygon",
                },
                {
                    "boundingPoly": [
                        {
                            "normalizedVertices": [
                                {"x": 0.34, "y": 0.73},
                                {"x": 0.34, "y": 0.12},
                                {"x": 0.73, "y": 0.12},
                                {"x": 0.73, "y": 0.73},
                            ]
                        }
                    ],
                    "categories": [{"name": "OBJECT_A", "confidence": 100}],
                    "mid": "second",
                    "type": "polygon",
                },
            ]
        }
    }

    result = kili.create_predictions(
        project_id=project_id,
        external_id_array=new_external_ids,
        model_name="model_demo",
        json_response_array=[json_response] * nb_assets,
    )

    # Then
    assert result == {"id": project_id}
    assert kili.count_labels(project_id=project_id) == nb_assets

    # When deleting assets
    kili.delete_many_from_dataset(asset_ids)

    # Then
    assert kili.count_assets(project_id=project_id) == 0
