from ...helpers import format_result
from .queries import GQL_GET_PROJECT, GQL_GET_PROJECTS


def get_projects(client, user_id: str):
    variables = {'userID': user_id}
    result = client.execute(GQL_GET_PROJECTS, variables)
    return format_result('data', result)


def get_project(client, project_id: str):
    variables = {'projectID': project_id}
    result = client.execute(GQL_GET_PROJECT, variables)
    return format_result('data', result)
