from ...helpers import format_result
from .queries import GQL_GET_LOCKS


def get_locks(client, project_id: str):
    variables = {'projectID': project_id}
    result = client.execute(GQL_GET_LOCKS, variables)
    return format_result('data', result)
