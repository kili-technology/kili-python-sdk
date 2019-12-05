from ..helper import format_result


def delete_locks(client, asset_id: str):
    result = client.execute('''
    mutation {
      deleteLocks(assetID: "%s") {
        id
      }
    }
    ''' % (asset_id))
    return format_result('deleteLocks', result)
