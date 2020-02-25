from ...helpers import format_result
from .queries import GQL_DELETE_LOCKS


def delete_locks(client, asset_id: str):
    variables = {'assetID': asset_id}
    result = client.execute(GQL_DELETE_LOCKS, variables)
    return format_result('data', result)
