from kili.domain.project import ProjectFilters


def projects(filters: ProjectFilters, *args, **kwargs) -> list[dict]:
    project_id = filters.id

    if project_id == "yolo!":
        return [{"jsonInterface": {"jobs": {"JOB_0": {}}}}]

    if project_id == "pid1":
        return [{"jsonInterface": {"jobs": {"Job1": {}}}}]

    return []


def project(project_id, *args, **kwargs):
    if project_id == "yolo!":
        return {"jsonInterface": {"jobs": {"JOB_0": {}}}}

    if project_id == "pid1":
        return {"jsonInterface": {"jobs": {"Job1": {}}}}

    return {}
