"""
Fake Kili object
"""

from test.services.export.fakes.fake_data import asset_image
from typing import List, Optional


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
    ):
        """
        Fake assets
        """
        _ = fields, label_type_in, asset_id_in, disable_tqdm
        if project_id == "object_detection":
            return [asset_image]
        elif project_id == "text_classification":
            return []
        else:
            return []

    def projects(self, project_id: str, fields: List[str], disable_tqdm: bool = False):
        """
        Fake projects
        """
        _ = fields, disable_tqdm
        if project_id == "object_detection":
            job_payload = {
                "mlTask": "OBJECT_DETECTION",
                "tools": ["rectangle"],
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

        else:
            return []
