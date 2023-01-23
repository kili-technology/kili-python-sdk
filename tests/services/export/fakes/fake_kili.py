"""
Fake Kili object
"""

from unittest.mock import MagicMock

from kili.orm import Asset
from tests.services.export.fakes.fake_data import (
    asset_image_1,
    asset_image_1_without_annotation,
    asset_image_2,
    asset_video_content_no_json_content,
    asset_video_no_content_and_json_content,
)


class FakeAuth:
    api_key = ""
    api_endpoint = "http://content-repository"
    client = MagicMock()


def mocked_ProjectQuery(where, _fields, _options):
    """
    Fake projects
    """
    project_id = where.project_id
    if project_id in ["object_detection", "object_detection_with_empty_annotation"]:
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
        json_interface = {
            "jobs": {
                "JOB_0": job_payload,
                "JOB_1": job_payload,
                "JOB_2": job_payload,
                "JOB_3": job_payload,
            }
        }
        return [
            {
                "title": "test OD project",
                "id": "object_detection",
                "description": "This is a test project",
                "jsonInterface": json_interface,
                "inputType": "IMAGE",
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
                "id": "object_detection_video_project_id",
                "description": "This is a test project",
                "jsonInterface": json_interface,
                "inputType": "VIDEO",
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
                "id": "text_classification",
                "description": "This is a TC test project",
                "jsonInterface": json_interface,
                "inputType": "TEXT",
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
                "id": "semantic_segmentation",
                "description": "This is a semantic segmentation test project",
                "jsonInterface": json_interface,
                "inputType": "IMAGE",
            }
        ]
    else:
        return []


def mocked_AssetQuery(where, _fields, _options, post_call_function):
    """
    Fake assets
    """
    project_id = where.project_id

    def _assets():
        if project_id == "object_detection":
            return [Asset(asset_image_1)]
        elif project_id == "object_detection_with_empty_annotation":
            return [Asset(asset_image_1_without_annotation)]
        elif project_id == "text_classification":
            return []
        elif project_id == "semantic_segmentation":
            return [
                Asset(asset_image_1),
                Asset(asset_image_2),
            ]
        elif project_id == "object_detection_video_project":
            return [
                Asset(asset_video_content_no_json_content),
                Asset(asset_video_no_content_and_json_content),
            ]
        else:
            return []

    if post_call_function:
        return post_call_function(_assets())
    return _assets()


class FakeKili:
    """
    Handke .assets and .project methods of Kili
    """

    auth = FakeAuth()
