"""Module to test validation of jsonResponse in the backend."""


import pytest
from gql.transport import exceptions

from kili.client import Kili
from kili.exceptions import GraphQLError


@pytest.fixture
def kili() -> Kili:
    return Kili()


@pytest.fixture()
def image_bbox_project(kili):
    interface = {
        "jobs": {
            "JOB_0": {
                "content": {
                    "categories": {
                        "OBJECT_A": {
                            "children": [],
                            "name": "Object A",
                        },
                        "OBJECT_B": {
                            "children": [],
                            "name": "Object B",
                        },
                    },
                    "input": "radio",
                },
                "instruction": "Categories",
                "isChild": False,
                "tools": ["rectangle"],
                "mlTask": "OBJECT_DETECTION",
                "models": {},
                "isVisible": True,
                "required": 1,
                "isNew": False,
            }
        }
    }

    project = kili.create_project(
        input_type="IMAGE",
        json_interface=interface,
        title="test_invalidation_bbox",
        description="test_invalidation_bbox",
    )

    kili.append_many_to_dataset(
        project_id=project["id"],
        content_array=[
            "https://storage.googleapis.com/label-public-staging/car/car_1.jpg",
        ],
        external_id_array=["1"],
    )
    yield project

    kili.delete_project(project["id"])


@pytest.mark.skip(reason="jsonResponse validation disabled on backend for now")
def test_json_response_with_wrong_bbox_responses(kili, image_bbox_project):
    with pytest.raises(GraphQLError) as exc_info:
        wrong_category_json_response = {
            "JOB_0": {
                "annotations": [
                    {
                        "boundingPoly": [
                            {
                                "normalizedVertices": [
                                    {"x": 0.437473570026755, "y": 0.662407024077585},
                                    {"x": 0.437473570026755, "y": 0.28769191191267807},
                                    {"x": 0.7235387616200971, "y": 0.28769191191267807},
                                    {"x": 0.7235387616200971, "y": 0.662407024077585},
                                ]
                            }
                        ],
                        "categories": [{"name": "DOES NOT EXIST"}],
                        "type": "rectangle",
                        "children": {},
                    }
                ]
            }
        }
        kili.append_labels(
            project_id=image_bbox_project["id"],
            asset_external_id_array=["1"],
            json_response_array=[wrong_category_json_response],
        )

    assert isinstance(exc_info.value.__cause__, exceptions.TransportQueryError)
    assert "jsonResponseMalformed" in str(exc_info.value.__cause__)

    with pytest.raises(GraphQLError):
        wrong_job_name_json_response = {
            "DOES NOT EXIST": {
                "annotations": [
                    {
                        "boundingPoly": [
                            {
                                "normalizedVertices": [
                                    {"x": 0.437473570026755, "y": 0.662407024077585},
                                    {"x": 0.437473570026755, "y": 0.28769191191267807},
                                    {"x": 0.7235387616200971, "y": 0.28769191191267807},
                                    {"x": 0.7235387616200971, "y": 0.662407024077585},
                                ]
                            }
                        ],
                        "categories": [{"name": "OBJECT_A"}],
                        "type": "rectangle",
                        "children": {},
                    }
                ]
            }
        }
        kili.append_labels(
            project_id=image_bbox_project["id"],
            asset_external_id_array=["1"],
            json_response_array=[wrong_job_name_json_response],
        )

    assert isinstance(exc_info.value.__cause__, exceptions.TransportQueryError)
    assert "jsonResponseMalformed" in str(exc_info.value.__cause__)
