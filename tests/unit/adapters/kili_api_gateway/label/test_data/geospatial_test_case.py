"""GEOSPATIAL test case: object detection on a geoTIFF (no frames).

The jsonResponse is a flat, job-keyed dict (there is no frame indexing for
geospatial projects) with coordinates expressed as longitude/latitude.
"""

json_interface = {
    "jobs": {
        "BUILDING_DETECTION_JOB": {
            "content": {
                "categories": {
                    "BUILDING": {"children": [], "name": "Building", "color": "#733AFB"},
                },
                "input": "radio",
            },
            "instruction": "Detect buildings",
            "isChild": False,
            "tools": ["polygon"],
            "mlTask": "OBJECT_DETECTION",
            "isVisible": True,
            "required": 0,
        },
        "TREE_JOB": {
            "content": {
                "categories": {
                    "TREE": {"children": [], "name": "Tree", "color": "#3CD876"},
                },
                "input": "radio",
            },
            "instruction": "Locate trees",
            "isChild": False,
            "tools": ["marker"],
            "mlTask": "OBJECT_DETECTION",
            "isVisible": True,
            "required": 0,
        },
    }
}

expected_json_resp = {
    "BUILDING_DETECTION_JOB": {
        "annotations": [
            {
                "children": {},
                "boundingPoly": [
                    {
                        "normalizedVertices": [
                            {"x": 4.398223, "y": 52.248060},
                            {"x": 4.398512, "y": 52.248060},
                            {"x": 4.398512, "y": 52.248341},
                            {"x": 4.398223, "y": 52.248341},
                        ]
                    }
                ],
                "categories": [{"name": "BUILDING"}],
                "mid": "20231031123948352-1",
                "type": "polygon",
            }
        ]
    },
    "TREE_JOB": {
        "annotations": [
            {
                "children": {},
                "point": {"x": 4.371029, "y": 52.241662},
                "categories": [{"name": "TREE"}],
                "mid": "20231031123948352-2",
                "type": "marker",
            }
        ]
    },
}
