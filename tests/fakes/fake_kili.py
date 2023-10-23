"""Fake Kili object."""

from copy import deepcopy
from unittest.mock import MagicMock

from kili.adapters.http_client import HttpClient
from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.core.graphql.operations.project.queries import ProjectWhere
from tests.fakes.fake_data import (
    asset_image_1,
    asset_image_1_with_classification,
    asset_image_1_without_annotation,
    asset_image_2,
    asset_image_no_content,
    asset_video_content_no_json_content,
    asset_video_no_content_and_json_content,
)


class FakeKili:
    api_key = ""
    api_endpoint = "http://content-repository"
    graphql_client = MagicMock()
    http_client = HttpClient(
        kili_endpoint="https://fake_endpoint.kili-technology.com", api_key="", verify=True
    )
    kili_api_gateway = MagicMock()
    kili_api_gateway.http_client = http_client


def mocked_ProjectQuery(where, _fields, _options):
    """Fake projects."""
    project_id = where.project_id
    if project_id in [
        "object_detection",
        "object_detection_with_empty_annotation",
        "object_detection_cloud_storage",
        "object_detection_with_classification",
        "object_detection_with_2500_assets",
        "object_detection_with_classification",
    ]:
        job_payload = {
            "mlTask": "OBJECT_DETECTION",
            "tools": ["rectangle"],
            "instruction": "Categories",
            "required": 1 if project_id == "object_detection" else 0,
            "isChild": False,
            "content": {
                "categories": {
                    "OBJECT_A": {
                        "name": "OBJECT A",
                    },
                    "OBJECT_B": {
                        "name": "OBJECT B",
                    },
                },
                "input": "radio",
            },
        }

        irrelevant_job_payload = {
            "mlTask": "CLASSIFICATION",
            "tools": [],
            "instruction": "classif",
            "required": 0,
            "isChild": False,
            "content": {
                "categories": {
                    "OBJECT_C": {
                        "name": "OBJECT C",
                    },
                    "OBJECT_D": {
                        "name": "OBJECT D",
                    },
                },
                "input": "radio",
            },
        }

        json_interface = {
            "jobs": {
                "JOB_0": job_payload,
                "JOB_1": job_payload,
                "JOB_2": job_payload,
                "JOB_3": job_payload,
                "JOB_4": irrelevant_job_payload,
            }
        }
        return [
            {
                "title": "test OD project",
                "id": project_id,
                "description": "This is a test project",
                "jsonInterface": json_interface,
                "inputType": "IMAGE",
                "dataConnections": None,
            }
        ]
    elif project_id == "object_detection_video_project":
        json_interface = {
            "jobs": {
                "JOB_0": {
                    "content": {
                        "categories": {
                            "OBJECT_A": {"children": [], "color": "#472CED", "name": "A"},
                            "OBJECT_B": {"children": [], "name": "B", "color": "#5CE7B7"},
                        },
                        "input": "radio",
                    },
                    "instruction": "dfgdfg",
                    "mlTask": "OBJECT_DETECTION",
                    "required": 1,
                    "tools": ["rectangle"],
                    "isChild": False,
                    "models": {"tracking": {}},
                }
            }
        }
        return [
            {
                "title": "test OD video project",
                "id": project_id,
                "description": "This is a test project",
                "jsonInterface": json_interface,
                "inputType": "VIDEO",
                "dataConnections": None,
            }
        ]
    elif project_id == "text_classification":
        job_payload = {
            "mlTask": "CLASSIFICATION",
            "instruction": "Categories",
            "required": 1,
            "isChild": False,
            "content": {
                "categories": {
                    "OBJECT_A": {
                        "name": "OBJECT A",
                    },
                    "OBJECT_B": {
                        "name": "OBJECT B",
                    },
                },
                "input": "radio",
            },
        }
        json_interface = {
            "jobs": {
                "JOB_0": job_payload,
            }
        }

        return [
            {
                "title": "test text project",
                "id": project_id,
                "description": "This is a TC test project",
                "jsonInterface": json_interface,
                "inputType": "TEXT",
                "dataConnections": None,
            }
        ]
    elif project_id == "semantic_segmentation":
        job_payload = {
            "content": {
                "categories": {
                    "OBJECT_A": {
                        "children": [],
                        "name": "Object A",
                        "color": "#733AFB",
                        "id": "category1",
                    },
                    "OBJECT_B": {
                        "children": [],
                        "name": "Object B",
                        "color": "#3CD876",
                        "id": "category2",
                    },
                },
                "input": "radio",
            },
            "instruction": "Categories",
            "isChild": False,
            "tools": ["semantic"],
            "mlTask": "OBJECT_DETECTION",
            "models": {"interactive-segmentation": {}},
            "isVisible": True,
            "required": 1,
            "isNew": False,
        }
        json_interface = {
            "jobs": {
                "JOB_0": job_payload,
            }
        }

        return [
            {
                "title": "segmentation",
                "id": project_id,
                "description": "This is a semantic segmentation test project",
                "jsonInterface": json_interface,
                "inputType": "IMAGE",
                "dataConnections": None,
            }
        ]
    else:
        return []


def mocked_kili_api_gateway_get_project(project_id, fields):
    return mocked_ProjectQuery(
        ProjectWhere(project_id=project_id), fields, QueryOptions(disable_tqdm=False)
    )[0]


def mocked_AssetQuery(where, _fields, _options, post_call_function=None):
    """Fake assets."""
    project_id = where.project_id

    if project_id == "object_detection":
        ret = [asset_image_1]
    elif project_id == "object_detection_with_empty_annotation":
        ret = [asset_image_1_without_annotation]
    elif project_id == "object_detection_with_classification":
        ret = [asset_image_1_with_classification]
    elif project_id == "text_classification":
        ret = []
    elif project_id == "semantic_segmentation":
        ret = [asset_image_1, asset_image_2]
    elif project_id == "object_detection_cloud_storage":
        ret = [asset_image_no_content, asset_image_1]
    elif project_id == "object_detection_video_project":
        ret = [asset_video_content_no_json_content, asset_video_no_content_and_json_content]
    elif project_id == "object_detection_2500_assets":
        ret = [{**asset_image_1, "id": f"{i}", "externalId": f"ext-{i}"} for i in range(2500)]
    else:
        ret = []

    if post_call_function:
        return post_call_function(ret)

    return deepcopy(ret)


def mocked_AssetQuery_count(where) -> int:
    return len(mocked_AssetQuery(where, None, None, None))
