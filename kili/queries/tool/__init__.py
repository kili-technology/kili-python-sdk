from ...helpers import format_result
from .queries import GQL_GET_TOOLS


def get_tools(client, project_id: str):
    variables = {'projectID': project_id}
    result = client.execute(GQL_GET_TOOLS, variables)
    return format_result('data', result)
