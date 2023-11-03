json_interface = {
    "jobs": {
        "JOB_0": {
            "content": {
                "categories": {
                    "OBJECT_A": {"children": ["JOB_1"], "name": "Train", "color": "#733AFB"}
                },
                "input": "radio",
            },
            "instruction": "Track objects A and B",
            "isChild": False,
            "tools": ["rectangle"],
            "mlTask": "OBJECT_DETECTION",
            "models": {"tracking": {}},
            "isVisible": True,
            "required": 0,
        },
        "JOB_1": {
            "content": {
                "categories": {
                    "IS_THE OBJECT OCCLUDED?": {"children": [], "name": "Is the object occluded?"}
                },
                "input": "checkbox",
            },
            "instruction": "",
            "isChild": True,
            "mlTask": "CLASSIFICATION",
            "models": {},
            "isVisible": True,
            "required": 0,
        },
    }
}

bbox_1 = [
    {"x": 0.37300837378966817, "y": 0.756392223998645},
    {"x": 0.37300837378966817, "y": 0.5735538392639435},
    {"x": 0.4899435385888102, "y": 0.5735538392639435},
    {"x": 0.4899435385888102, "y": 0.756392223998645},
]

bbox_2 = [
    {"x": 0.3582470662812001, "y": 0.7120201400492349},
    {"x": 0.3958786574252113, "y": 0.5418608506018523},
    {"x": 0.5047048460972782, "y": 0.6179259232133538},
    {"x": 0.46707325495326707, "y": 0.7880852126607364},
]

bbox_3 = [
    {"x": 0.37336594428323905, "y": 0.7571099568850419},
    {"x": 0.3726536081515613, "y": 0.5742759577878287},
    {"x": 0.4895859680952394, "y": 0.5728361063775467},
    {"x": 0.49029830422691717, "y": 0.7556701054747601},
]

bbox_4 = [
    {"x": 0.3053819634769522, "y": 0.5419589505028481},
    {"x": 0.4038254704845748, "y": 0.4890331805536148},
    {"x": 0.4376744001834186, "y": 0.6880179239839324},
    {"x": 0.33923089317579597, "y": 0.740943693933166},
]

annotations = [
    {
        "id": "277417a2-c99d-4ae3-aff1-472094315c56",
        "job": "JOB_0",
        "path": [],
        "labelId": "cloibot0x0329083fg7jxfea9",
        "keyAnnotations": [
            {
                "id": "277417a2-c99d-4ae3-aff1-472094315c56-0",
                "frame": 0,
                "isPrediction": False,
                "annotationValue": {"vertices": [[bbox_1]]},
            },
            {
                "id": "277417a2-c99d-4ae3-aff1-472094315c56-3",
                "frame": 3,
                "isPrediction": False,
                "annotationValue": {"vertices": [[bbox_2]]},
            },
            {
                "id": "277417a2-c99d-4ae3-aff1-472094315c56-9",
                "frame": 9,
                "isPrediction": False,
                "annotationValue": {"vertices": [[bbox_3]]},
            },
            {
                "id": "277417a2-c99d-4ae3-aff1-472094315c56-7",
                "frame": 7,
                "isPrediction": False,
                "annotationValue": {"vertices": [[bbox_4]]},
            },
        ],
        "frames": [{"start": 0, "end": 9}],
        "name": "Train 1",
        "mid": "20231103085506560-87322",
        "category": "OBJECT_A",
    },
    {
        "id": "946a8b83-cac3-4400-af04-0ec0895a3e75",
        "job": "JOB_1",
        "path": [["277417a2-c99d-4ae3-aff1-472094315c56", "OBJECT_A"]],
        "labelId": "cloibot0x0329083fg7jxfea9",
        "keyAnnotations": [
            {
                "id": "946a8b83-cac3-4400-af04-0ec0895a3e75-7",
                "frame": 7,
                "isPrediction": False,
                "annotationValue": {"categories": ["IS_THE OBJECT OCCLUDED?"]},
            }
        ],
        "frames": [{"start": 7, "end": 8}],
    },
]

expected_json_resp = {
    "0": {
        "JOB_0": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": True,
                    "boundingPoly": [{"normalizedVertices": bbox_1}],
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231103085506560-87322",
                    "type": "rectangle",
                }
            ]
        },
    },
    "1": {
        "JOB_0": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": []}],
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231103085506560-87322",
                    "type": "rectangle",
                }
            ]
        }
    },
    "2": {
        "JOB_0": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": []}],
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231103085506560-87322",
                    "type": "rectangle",
                }
            ]
        }
    },
    "3": {
        "JOB_0": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": True,
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231103085506560-87322",
                    "type": "rectangle",
                    "boundingPoly": [{"normalizedVertices": bbox_2}],
                }
            ]
        }
    },
    "4": {
        "JOB_0": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": False,
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231103085506560-87322",
                    "type": "rectangle",
                    "boundingPoly": [{"normalizedVertices": []}],
                }
            ]
        }
    },
    "5": {
        "JOB_0": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": False,
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231103085506560-87322",
                    "type": "rectangle",
                    "boundingPoly": [{"normalizedVertices": []}],
                }
            ]
        }
    },
    "6": {
        "JOB_0": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": False,
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231103085506560-87322",
                    "type": "rectangle",
                    "boundingPoly": [{"normalizedVertices": []}],
                }
            ]
        }
    },
    "7": {
        "JOB_0": {
            "annotations": [
                {
                    "children": {
                        "JOB_1": {
                            "categories": [{"name": "IS_THE OBJECT OCCLUDED?"}],
                            "isKeyFrame": True,
                        }
                    },
                    "isKeyFrame": True,
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231103085506560-87322",
                    "type": "rectangle",
                    "boundingPoly": [{"normalizedVertices": bbox_3}],
                }
            ]
        }
    },
    "8": {
        "JOB_0": {
            "annotations": [
                {
                    "children": {
                        "JOB_1": {
                            "categories": [{"name": "IS_THE OBJECT OCCLUDED?"}],
                            "isKeyFrame": False,
                        }
                    },
                    "isKeyFrame": False,
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231103085506560-87322",
                    "type": "rectangle",
                    "boundingPoly": [{"normalizedVertices": []}],
                }
            ]
        }
    },
    "9": {
        "JOB_0": {
            "annotations": [
                {
                    "children": {"JOB_1": {"categories": [], "isKeyFrame": True}},
                    "isKeyFrame": True,
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231103085506560-87322",
                    "type": "rectangle",
                    "boundingPoly": [{"normalizedVertices": bbox_4}],
                }
            ]
        }
    },
}
