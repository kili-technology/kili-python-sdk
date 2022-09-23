def mocked__project_assets(project_id=None, **_):
    if project_id in ["object_detection", "project_id"]:
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

        return [
            {
                "latestLabel": {
                    "jsonResponse": job_object_detection,
                    "author": {"firstname": "Jean-Pierre", "lastname": "Dupont"},
                },
                "externalId": "car_1",
                "content": "https://storage.googleapis.com/label-public-staging/car/car_1.jpg",
                "jsonContent": "",
            }
        ]
    else:
        return [
            {"externalId": "asset1"},
            {"externalId": "asset2"},
            {"externalId": "asset3"},
            {"externalId": "asset4"},
            {"externalId": "asset5"},
            {"externalId": "asset6"},
        ]
