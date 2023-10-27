from typing import Dict, List

from kili.domain.project import ProjectFilters


def projects(filters: ProjectFilters, _fields, _options) -> List[Dict]:
    project_id = filters.id

    if project_id == "yolo!":
        return [{"jsonInterface": {"jobs": {"JOB_0": {}}}}]

    if project_id == "pid1":
        return [{"jsonInterface": {"jobs": {"Job1": {}}}}]

    return []
