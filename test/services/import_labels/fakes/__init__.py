from typing import Dict, List


def projects(project_id, fields) -> List[Dict]:
    _ = fields
    if project_id == "yolo!":
        return [{"jsonInterface": {"JOB_0": {}}}]
    elif project_id == "pid1":
        return [{"jsonInterface": {"Job1": {}}}]
    else:
        return []
