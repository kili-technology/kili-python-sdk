from typing import Dict, List


def projects(where, _fields, _options) -> List[Dict]:
    project_id = where.project_id
    if project_id == "yolo!":
        return [{"jsonInterface": {"jobs": {"JOB_0": {}}}}]
    elif project_id == "pid1":
        return [{"jsonInterface": {"jobs": {"Job1": {}}}}]
    else:
        return []
