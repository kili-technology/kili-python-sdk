def mocked__projects(project_id=None, **_):
    if project_id == "text_project":
        return [{"id": "text_project", "inputType": "TEXT"}]
    if project_id == "image_project":
        return [{"id": "image_project", "inputType": "IMAGE"}]
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
    if project_id == "frame_project":
        return [{"id": "frame_project", "inputType": "VIDEO"}]
    if project_id is None:
        return [
            {
                "id": "text_project",
                "title": "text_project",
                "description": " a project with text",
                "numberOfAssets": 10,
                "numberOfRemainingAssets": 10,
            },
            {
                "id": "image_project",
                "title": "image_project",
                "description": " a project with image",
                "numberOfAssets": 0,
                "numberOfRemainingAssets": 0,
            },
            {
                "id": "frame_project",
                "title": "frame_project",
                "description": " a project with frame",
                "numberOfAssets": 10,
                "numberOfRemainingAssets": 0,
            },
        ]
    if project_id == "project_id":
        return [
            {
                "title": "project title",
                "id": "project_id",
                "description": "description test",
                "numberOfAssets": 49,
                "numberOfRemainingAssets": 29,
                "numberOfReviewedAssets": 0,
                "numberOfSkippedAssets": 0,
                "numberOfOpenIssues": 3,
                "numberOfSolvedIssues": 2,
                "numberOfOpenQuestions": 0,
                "numberOfSolvedQuestions": 2,
                "honeypotMark": None,
                "consensusMark": None,
            }
        ]
