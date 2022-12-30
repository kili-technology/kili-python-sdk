from typing import Dict

from kili.orm import Label
from kili.services.export.types import JobCategory

job_category_a: JobCategory = JobCategory(category_name="OBJECT_A", id=0, job_id="JOB_0")
job_category_b: JobCategory = JobCategory(category_name="OBJECT_B", id=1, job_id="JOB_0")
category_ids: Dict[str, JobCategory] = {
    "JOB_0__OBJECT_A": job_category_a,
    "JOB_0__OBJECT_B": job_category_b,
}
job_object_detection = {
    "JOB_0": {
        "annotations": [
            {
                "categories": [{"confidence": 100, "name": "OBJECT_A"}],
                "jobName": "JOB_0",
                "mid": "2022040515434712-7532",
                "mlTask": "OBJECT_DETECTION",
                "boundingPoly": [
                    {
                        "normalizedVertices": [
                            {"x": 0.16504140348233334, "y": 0.7986938935103378},
                            {"x": 0.16504140348233334, "y": 0.2605618833516984},
                            {"x": 0.8377886490672706, "y": 0.2605618833516984},
                            {"x": 0.8377886490672706, "y": 0.7986938935103378},
                        ]
                    }
                ],
                "type": "rectangle",
                "children": {},
            }
        ]
    }
}
asset_image_1 = {
    "latestLabel": {
        "jsonResponse": job_object_detection,
        "author": {"firstname": "Jean-Pierre", "lastname": "Dupont"},
    },
    "externalId": "car_1",
    "content": "https://storage.googleapis.com/label-public-staging/car/car_1.jpg",
    "jsonContent": "",
}

asset_image_1_without_annotation = {
    "latestLabel": {
        "jsonResponse": {},
        "author": {"firstname": "Jean-Pierre", "lastname": "Dupont"},
    },
    "externalId": "car_1",
    "content": "https://storage.googleapis.com/label-public-staging/car/car_1.jpg",
    "jsonContent": "",
}

asset_image_2 = {
    "latestLabel": {
        "jsonResponse": job_object_detection,
        "author": {"firstname": "Jean-Pierre", "lastname": "Dupont"},
    },
    "externalId": "car_2",
    "content": "https://storage.googleapis.com/label-public-staging/car/car_2.jpg",
    "jsonContent": "",
}


asset_video = {
    "latestLabel": {
        "jsonResponse": {
            "0": job_object_detection,
            "1": job_object_detection,
            "2": job_object_detection,
            "3": job_object_detection,
        }
    },
    "externalId": "video_1",
    "content": "https://storage.googleapis.com/label-public-staging/video1/video1.mp4",
    "jsonContent": "",
}

asset_video_frames = {
    "latestLabel": {
        "jsonResponse": [
            {
                "0": job_object_detection,
                "1": job_object_detection,
                "2": job_object_detection,
                "3": job_object_detection,
            },
            {
                "0": job_object_detection,
                "1": job_object_detection,
                "2": job_object_detection,
                "3": job_object_detection,
            },
        ]
    },
    "externalId": "video_1",
    "content": "https://storage.googleapis.com/label-public-staging/video1/video1.mp4",
    "jsonContent": "",
}

# Data for Kili format export test
job_0 = {
    "JOB_0": {
        "categories": [{"confidence": 100, "name": "OBJECT_A"}],
    }
}

frame_json_response = {"0": job_0, "1": job_0, "2": job_0}

frame_default_label = Label({"jsonResponse": frame_json_response, "labelType": "DEFAULT"})
frame_autosave_label = Label({"jsonResponse": frame_json_response, "labelType": "AUTOSAVE"})

kili_format_frame_asset = {
    "labels": [
        frame_default_label,
        frame_autosave_label,
    ]
}

kili_format_expected_frame_asset_output = {
    "labels": [
        {
            "jsonResponse": {
                0: job_0,
                1: job_0,
                2: job_0,
            },
            "labelType": "DEFAULT",
        }
    ]
}
