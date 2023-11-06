json_interface = {
    "jobs": {
        "CLASSIFICATION_JOB": {
            "content": {
                "categories": {
                    "CAR": {"children": ["CLASSIFICATION_JOB_0"], "name": "Car"},
                    "TRUCK": {"children": ["TRANSCRIPTION_JOB"], "name": "Truck"},
                },
                "input": "checkbox",
            },
            "instruction": "Type",
            "mlTask": "CLASSIFICATION",
            "required": 0,
            "isChild": False,
        },
        "CLASSIFICATION_JOB_0": {
            "content": {
                "categories": {
                    "BLUE": {"children": {}, "name": "Blue"},
                    "GREEN": {"children": {}, "name": "Green"},
                },
                "input": "radio",
            },
            "instruction": "Color",
            "mlTask": "CLASSIFICATION",
            "required": 0,
            "isChild": True,
        },
        "TRANSCRIPTION_JOB": {
            "content": {"input": "textField"},
            "instruction": "Truck brand",
            "mlTask": "TRANSCRIPTION",
            "required": 0,
            "isChild": True,
        },
    }
}

annotations = [
    {
        "id": "f98a628f-4ef0-41bc-ab03-d5c7ca6d2e15",
        "job": "CLASSIFICATION_JOB",
        "path": [],
        "labelId": "cloh004bg0019084z12v7b7qc",
        "frames": [{"start": 4, "end": 11}, {"start": 14, "end": 16}, {"start": 18, "end": 21}],
        "keyAnnotations": [
            {
                "id": "f98a628f-4ef0-41bc-ab03-d5c7ca6d2e15-4",
                "frame": 4,
                "isPrediction": False,
                "annotationValue": {"categories": ["TRUCK", "CAR"]},
            },
            {
                "id": "f98a628f-4ef0-41bc-ab03-d5c7ca6d2e15-14",
                "frame": 14,
                "isPrediction": False,
                "annotationValue": {"categories": ["CAR"]},
            },
            {
                "id": "f98a628f-4ef0-41bc-ab03-d5c7ca6d2e15-18",
                "frame": 18,
                "isPrediction": False,
                "annotationValue": {"categories": ["TRUCK"]},
            },
        ],
    },
    {
        "id": "0c2b0724-9fb1-42c1-a0b4-3cc9af0d4fb9",
        "job": "CLASSIFICATION_JOB_0",
        "path": [["f98a628f-4ef0-41bc-ab03-d5c7ca6d2e15", "CAR"]],
        "labelId": "cloh004bg0019084z12v7b7qc",
        "frames": [{"start": 4, "end": 11}, {"start": 14, "end": 16}],
        "keyAnnotations": [
            {
                "id": "0c2b0724-9fb1-42c1-a0b4-3cc9af0d4fb9-4",
                "frame": 4,
                "isPrediction": False,
                "annotationValue": {"categories": ["BLUE"]},
            },
            {
                "id": "0c2b0724-9fb1-42c1-a0b4-3cc9af0d4fb9-14",
                "frame": 14,
                "isPrediction": False,
                "annotationValue": {"categories": ["GREEN"]},
            },
        ],
    },
    {
        "id": "3de07f87-3f52-4a7a-829a-e262d7fdb749",
        "job": "TRANSCRIPTION_JOB",
        "path": [["f98a628f-4ef0-41bc-ab03-d5c7ca6d2e15", "TRUCK"]],
        "labelId": "cloh004bg0019084z12v7b7qc",
        "frames": [{"start": 4, "end": 11}, {"start": 18, "end": 21}],
        "keyAnnotations": [
            {
                "id": "3de07f87-3f52-4a7a-829a-e262d7fdb749-4",
                "frame": 4,
                "isPrediction": False,
                "annotationValue": {"text": "Benz"},
            },
            {
                "id": "3de07f87-3f52-4a7a-829a-e262d7fdb749-18",
                "frame": 18,
                "isPrediction": False,
                "annotationValue": {"text": "Mercedes"},
            },
        ],
    },
]

expected_json_resp = {
    "4": {
        "CLASSIFICATION_JOB": {
            "categories": [
                {
                    "name": "TRUCK",
                    "children": {"TRANSCRIPTION_JOB": {"isKeyFrame": True, "text": "Benz"}},
                },
                {
                    "name": "CAR",
                    "children": {
                        "CLASSIFICATION_JOB_0": {
                            "categories": [{"name": "BLUE"}],
                            "isKeyFrame": True,
                        }
                    },
                },
            ],
            "isKeyFrame": True,
        }
    },
    "5": {
        "CLASSIFICATION_JOB": {
            "categories": [
                {
                    "name": "TRUCK",
                    "children": {"TRANSCRIPTION_JOB": {"isKeyFrame": False, "text": "Benz"}},
                },
                {
                    "name": "CAR",
                    "children": {
                        "CLASSIFICATION_JOB_0": {
                            "categories": [{"name": "BLUE"}],
                            "isKeyFrame": False,
                        }
                    },
                },
            ],
            "isKeyFrame": False,
        }
    },
    "6": {
        "CLASSIFICATION_JOB": {
            "categories": [
                {
                    "name": "TRUCK",
                    "children": {"TRANSCRIPTION_JOB": {"isKeyFrame": False, "text": "Benz"}},
                },
                {
                    "name": "CAR",
                    "children": {
                        "CLASSIFICATION_JOB_0": {
                            "categories": [{"name": "BLUE"}],
                            "isKeyFrame": False,
                        }
                    },
                },
            ],
            "isKeyFrame": False,
        }
    },
    "7": {
        "CLASSIFICATION_JOB": {
            "categories": [
                {
                    "name": "TRUCK",
                    "children": {"TRANSCRIPTION_JOB": {"isKeyFrame": False, "text": "Benz"}},
                },
                {
                    "name": "CAR",
                    "children": {
                        "CLASSIFICATION_JOB_0": {
                            "categories": [{"name": "BLUE"}],
                            "isKeyFrame": False,
                        }
                    },
                },
            ],
            "isKeyFrame": False,
        }
    },
    "8": {
        "CLASSIFICATION_JOB": {
            "categories": [
                {
                    "name": "TRUCK",
                    "children": {"TRANSCRIPTION_JOB": {"isKeyFrame": False, "text": "Benz"}},
                },
                {
                    "name": "CAR",
                    "children": {
                        "CLASSIFICATION_JOB_0": {
                            "categories": [{"name": "BLUE"}],
                            "isKeyFrame": False,
                        }
                    },
                },
            ],
            "isKeyFrame": False,
        }
    },
    "9": {
        "CLASSIFICATION_JOB": {
            "categories": [
                {
                    "name": "TRUCK",
                    "children": {"TRANSCRIPTION_JOB": {"isKeyFrame": False, "text": "Benz"}},
                },
                {
                    "name": "CAR",
                    "children": {
                        "CLASSIFICATION_JOB_0": {
                            "categories": [{"name": "BLUE"}],
                            "isKeyFrame": False,
                        }
                    },
                },
            ],
            "isKeyFrame": False,
        }
    },
    "10": {
        "CLASSIFICATION_JOB": {
            "categories": [
                {
                    "name": "TRUCK",
                    "children": {"TRANSCRIPTION_JOB": {"isKeyFrame": False, "text": "Benz"}},
                },
                {
                    "name": "CAR",
                    "children": {
                        "CLASSIFICATION_JOB_0": {
                            "categories": [{"name": "BLUE"}],
                            "isKeyFrame": False,
                        }
                    },
                },
            ],
            "isKeyFrame": False,
        }
    },
    "11": {
        "CLASSIFICATION_JOB": {
            "categories": [
                {
                    "name": "TRUCK",
                    "children": {"TRANSCRIPTION_JOB": {"isKeyFrame": False, "text": "Benz"}},
                },
                {
                    "name": "CAR",
                    "children": {
                        "CLASSIFICATION_JOB_0": {
                            "categories": [{"name": "BLUE"}],
                            "isKeyFrame": False,
                        }
                    },
                },
            ],
            "isKeyFrame": False,
        }
    },
    "14": {
        "CLASSIFICATION_JOB": {
            "categories": [
                {
                    "name": "CAR",
                    "children": {
                        "CLASSIFICATION_JOB_0": {
                            "categories": [{"name": "GREEN"}],
                            "isKeyFrame": True,
                        }
                    },
                }
            ],
            "isKeyFrame": True,
        }
    },
    "15": {
        "CLASSIFICATION_JOB": {
            "categories": [
                {
                    "name": "CAR",
                    "children": {
                        "CLASSIFICATION_JOB_0": {
                            "categories": [{"name": "GREEN"}],
                            "isKeyFrame": False,
                        }
                    },
                }
            ],
            "isKeyFrame": False,
        }
    },
    "16": {
        "CLASSIFICATION_JOB": {
            "categories": [
                {
                    "name": "CAR",
                    "children": {
                        "CLASSIFICATION_JOB_0": {
                            "categories": [{"name": "GREEN"}],
                            "isKeyFrame": False,
                        }
                    },
                }
            ],
            "isKeyFrame": False,
        }
    },
    "18": {
        "CLASSIFICATION_JOB": {
            "categories": [
                {
                    "name": "TRUCK",
                    "children": {"TRANSCRIPTION_JOB": {"isKeyFrame": True, "text": "Mercedes"}},
                }
            ],
            "isKeyFrame": True,
        }
    },
    "19": {
        "CLASSIFICATION_JOB": {
            "categories": [
                {
                    "name": "TRUCK",
                    "children": {"TRANSCRIPTION_JOB": {"isKeyFrame": False, "text": "Mercedes"}},
                }
            ],
            "isKeyFrame": False,
        }
    },
    "20": {
        "CLASSIFICATION_JOB": {
            "categories": [
                {
                    "name": "TRUCK",
                    "children": {"TRANSCRIPTION_JOB": {"isKeyFrame": False, "text": "Mercedes"}},
                }
            ],
            "isKeyFrame": False,
        }
    },
    "21": {
        "CLASSIFICATION_JOB": {
            "categories": [
                {
                    "name": "TRUCK",
                    "children": {"TRANSCRIPTION_JOB": {"isKeyFrame": False, "text": "Mercedes"}},
                }
            ],
            "isKeyFrame": False,
        }
    },
}
