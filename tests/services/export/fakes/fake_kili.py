"""
Fake Kili object
"""

from typing import List, Optional

from kili.orm import Asset
from kili.queries.asset.helpers import get_post_assets_call_process
from tests.services.export.fakes.fake_data import (
    asset_image_1,
    asset_image_1_without_annotation,
    asset_image_2,
)


class FakeAuth:
    api_key = ""
    api_endpoint = "http://content-repository"


class FakeKili:
    """
    Handke .assets and .project methods of Kili
    """

    auth = FakeAuth()

    def assets(
        self,
        project_id: str,
        fields: List[str],
        label_type_in: Optional[List[str]] = None,
        asset_id_in: Optional[List[str]] = None,
        disable_tqdm: bool = False,
        download_media: Optional[bool] = None,
        local_media_dir: Optional[str] = None,
    ):
        """
        Fake assets
        """

        _ = fields, label_type_in, asset_id_in, disable_tqdm, local_media_dir

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
            else:
                return []

        post_call_process = get_post_assets_call_process(
            bool(download_media), local_media_dir, project_id
        )

        return post_call_process(_assets())

    def count_assets(self, project_id: str):
        """
        Count assets.
        """
        return len(self.assets(project_id=project_id, fields=[""]))

    def projects(
        self, project_id: str, fields: Optional[List[str]] = None, disable_tqdm: bool = False
    ):
        """
        Fake projects
        """
        _ = fields, disable_tqdm
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

    def count_projects(self, project_id: str) -> int:
        return len(self.projects(project_id=project_id))
