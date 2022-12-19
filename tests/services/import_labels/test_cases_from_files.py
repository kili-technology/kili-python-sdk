from unittest.mock import ANY

YOLO_V4_TEST_CASE = {
    "description": "AAU, I import assets with all the asset attributes in the CSV, yolo_v4",
    "inputs": {
        "labels": [
            {
                "yolo_data": [
                    [
                        1,
                        0.0889384562446663,
                        0.5530594818041775,
                        0.08369207111544572,
                        0.13280688368534332,
                    ],
                    [
                        3,
                        0.7116800205440644,
                        0.8181361143179348,
                        0.08755478209000467,
                        0.07899719805421301,
                    ],
                ],
                "path": "un_asset.txt",
            }
        ],
        "project_id": "yolo!",
        "target_job_name": "JOB_0",
        "meta_path": "yolo_classes.txt",
        "yolo_classes": [[0, "A"], [1, "B"], [2, "C"], [3, "D"]],
        "label_format": "yolo_v4",
    },
    "outputs": {
        "call": {
            "kili": ANY,
            "label_type": "DEFAULT",
            "model_name": None,
            "labels": [
                {
                    "json_response": {
                        "JOB_0": {
                            "annotations": [
                                {
                                    "boundingPoly": [
                                        {
                                            "normalizedVertices": [
                                                {
                                                    "x": 0.04709242068694344,
                                                    "y": 0.48665603996150586,
                                                },
                                                {
                                                    "x": 0.04709242068694344,
                                                    "y": 0.6194629236468492,
                                                },
                                                {
                                                    "x": 0.13078449180238916,
                                                    "y": 0.6194629236468492,
                                                },
                                                {
                                                    "x": 0.13078449180238916,
                                                    "y": 0.48665603996150586,
                                                },
                                            ]
                                        }
                                    ],
                                    "categories": [{"name": "B", "confidence": 100}],
                                },
                                {
                                    "boundingPoly": [
                                        {
                                            "normalizedVertices": [
                                                {
                                                    "x": 0.6679026294990621,
                                                    "y": 0.7786375152908283,
                                                },
                                                {
                                                    "x": 0.6679026294990621,
                                                    "y": 0.8576347133450413,
                                                },
                                                {
                                                    "x": 0.7554574115890668,
                                                    "y": 0.8576347133450413,
                                                },
                                                {
                                                    "x": 0.7554574115890668,
                                                    "y": 0.7786375152908283,
                                                },
                                            ]
                                        }
                                    ],
                                    "categories": [{"name": "D", "confidence": 100}],
                                },
                            ]
                        }
                    },
                    "asset_external_id": "un_asset",
                }
            ],
            "project_id": "yolo!",
        }
    },
}

YOLO_V5_TEST_CASE = YOLO_V4_TEST_CASE.copy()
YOLO_V5_TEST_CASE["inputs"]["label_format"] = "yolo_v5"
YOLO_V5_TEST_CASE[
    "description"
] = "AAU, I import assets with all the asset attributes in the CSV, yolo_v5"

YOLO_V7_TEST_CASE = YOLO_V4_TEST_CASE.copy()
YOLO_V7_TEST_CASE["inputs"]["label_format"] = "yolo_v7"
YOLO_V7_TEST_CASE[
    "description"
] = "AAU, I import assets with all the asset attributes in the CSV, yolo_v7"


TEST_CASES = [
    YOLO_V4_TEST_CASE,
    YOLO_V5_TEST_CASE,
    YOLO_V7_TEST_CASE,
    {
        "description": (
            "AAU, I import assets with the minimum amount of asset attributes in the CSV"
        ),
        "inputs": {
            "labels": [
                {
                    "yolo_data": [
                        [
                            1,
                            0.0889384562446663,
                            0.5530594818041775,
                            0.08369207111544572,
                            0.13280688368534332,
                        ],
                        [
                            3,
                            0.7116800205440644,
                            0.8181361143179348,
                            0.08755478209000467,
                            0.07899719805421301,
                        ],
                    ],
                    "path": "un_asset.txt",
                }
            ],
            "project_id": "yolo!",
            "target_job_name": "JOB_0",
            "meta_path": "yolo_classes.txt",
            "yolo_classes": [[0, "A"], [1, "B"], [2, "C"], [3, "D"]],
            "label_format": "yolo_v4",
        },
        "outputs": {
            "call": {
                "kili": ANY,
                "label_type": "DEFAULT",
                "model_name": None,
                "labels": [
                    {
                        "json_response": {
                            "JOB_0": {
                                "annotations": [
                                    {
                                        "boundingPoly": [
                                            {
                                                "normalizedVertices": [
                                                    {
                                                        "x": 0.04709242068694344,
                                                        "y": 0.48665603996150586,
                                                    },
                                                    {
                                                        "x": 0.04709242068694344,
                                                        "y": 0.6194629236468492,
                                                    },
                                                    {
                                                        "x": 0.13078449180238916,
                                                        "y": 0.6194629236468492,
                                                    },
                                                    {
                                                        "x": 0.13078449180238916,
                                                        "y": 0.48665603996150586,
                                                    },
                                                ]
                                            }
                                        ],
                                        "categories": [{"name": "B", "confidence": 100}],
                                    },
                                    {
                                        "boundingPoly": [
                                            {
                                                "normalizedVertices": [
                                                    {
                                                        "x": 0.6679026294990621,
                                                        "y": 0.7786375152908283,
                                                    },
                                                    {
                                                        "x": 0.6679026294990621,
                                                        "y": 0.8576347133450413,
                                                    },
                                                    {
                                                        "x": 0.7554574115890668,
                                                        "y": 0.8576347133450413,
                                                    },
                                                    {
                                                        "x": 0.7554574115890668,
                                                        "y": 0.7786375152908283,
                                                    },
                                                ]
                                            }
                                        ],
                                        "categories": [{"name": "D", "confidence": 100}],
                                    },
                                ]
                            }
                        },
                        "asset_external_id": "un_asset",
                    }
                ],
                "project_id": "yolo!",
            }
        },
    },
    {
        "description": (
            "AAU, I import assets with the minimum amount of asset attributes in the CSV and ids"
        ),
        "inputs": {
            "labels": [
                {
                    "yolo_data": [
                        [
                            1,
                            0.0889384562446663,
                            0.5530594818041775,
                            0.08369207111544572,
                            0.13280688368534332,
                        ],
                        [
                            3,
                            0.7116800205440644,
                            0.8181361143179348,
                            0.08755478209000467,
                            0.07899719805421301,
                        ],
                    ],
                    "path": "id1.txt",
                }
            ],
            "project_id": "yolo!",
            "target_job_name": "JOB_0",
            "meta_path": "yolo_classes.txt",
            "yolo_classes": [[0, "A"], [1, "B"], [2, "C"], [3, "D"]],
            "label_format": "yolo_v4",
        },
        "outputs": {
            "call": {
                "kili": ANY,
                "label_type": "DEFAULT",
                "model_name": None,
                "labels": [
                    {
                        "json_response": {
                            "JOB_0": {
                                "annotations": [
                                    {
                                        "boundingPoly": [
                                            {
                                                "normalizedVertices": [
                                                    {
                                                        "x": 0.04709242068694344,
                                                        "y": 0.48665603996150586,
                                                    },
                                                    {
                                                        "x": 0.04709242068694344,
                                                        "y": 0.6194629236468492,
                                                    },
                                                    {
                                                        "x": 0.13078449180238916,
                                                        "y": 0.6194629236468492,
                                                    },
                                                    {
                                                        "x": 0.13078449180238916,
                                                        "y": 0.48665603996150586,
                                                    },
                                                ]
                                            }
                                        ],
                                        "categories": [{"name": "B", "confidence": 100}],
                                    },
                                    {
                                        "boundingPoly": [
                                            {
                                                "normalizedVertices": [
                                                    {
                                                        "x": 0.6679026294990621,
                                                        "y": 0.7786375152908283,
                                                    },
                                                    {
                                                        "x": 0.6679026294990621,
                                                        "y": 0.8576347133450413,
                                                    },
                                                    {
                                                        "x": 0.7554574115890668,
                                                        "y": 0.8576347133450413,
                                                    },
                                                    {
                                                        "x": 0.7554574115890668,
                                                        "y": 0.7786375152908283,
                                                    },
                                                ]
                                            }
                                        ],
                                        "categories": [{"name": "D", "confidence": 100}],
                                    },
                                ]
                            }
                        },
                        "asset_external_id": "id1",
                    }
                ],
                "project_id": "yolo!",
            }
        },
    },
    {
        "description": (
            "AAU, I import assets with the minimum amount of asset attributes in the CSV and ids"
        ),
        "inputs": {
            "labels": [
                {
                    "yolo_data": [
                        [
                            1,
                            0.0889384562446663,
                            0.5530594818041775,
                            0.08369207111544572,
                            0.13280688368534332,
                        ],
                        [
                            3,
                            0.7116800205440644,
                            0.8181361143179348,
                            0.08755478209000467,
                            0.07899719805421301,
                        ],
                    ],
                    "path": "id1.txt",
                }
            ],
            "project_id": "yolo!",
            "target_job_name": "JOB_0",
            "meta_path": "yolo_classes.txt",
            "yolo_classes": [[0, "A"], [1, "B"], [2, "C"], [3, "D"]],
            "label_format": "yolo_v7",
        },
        "outputs": {
            "call": {
                "kili": ANY,
                "label_type": "DEFAULT",
                "model_name": None,
                "labels": [
                    {
                        "json_response": {
                            "JOB_0": {
                                "annotations": [
                                    {
                                        "boundingPoly": [
                                            {
                                                "normalizedVertices": [
                                                    {
                                                        "x": 0.04709242068694344,
                                                        "y": 0.48665603996150586,
                                                    },
                                                    {
                                                        "x": 0.04709242068694344,
                                                        "y": 0.6194629236468492,
                                                    },
                                                    {
                                                        "x": 0.13078449180238916,
                                                        "y": 0.6194629236468492,
                                                    },
                                                    {
                                                        "x": 0.13078449180238916,
                                                        "y": 0.48665603996150586,
                                                    },
                                                ]
                                            }
                                        ],
                                        "categories": [{"name": "B", "confidence": 100}],
                                    },
                                    {
                                        "boundingPoly": [
                                            {
                                                "normalizedVertices": [
                                                    {
                                                        "x": 0.6679026294990621,
                                                        "y": 0.7786375152908283,
                                                    },
                                                    {
                                                        "x": 0.6679026294990621,
                                                        "y": 0.8576347133450413,
                                                    },
                                                    {
                                                        "x": 0.7554574115890668,
                                                        "y": 0.8576347133450413,
                                                    },
                                                    {
                                                        "x": 0.7554574115890668,
                                                        "y": 0.7786375152908283,
                                                    },
                                                ]
                                            }
                                        ],
                                        "categories": [{"name": "D", "confidence": 100}],
                                    },
                                ]
                            }
                        },
                        "asset_external_id": "id1",
                    }
                ],
                "project_id": "yolo!",
            }
        },
    },
]
