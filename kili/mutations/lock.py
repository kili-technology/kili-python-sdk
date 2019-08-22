from ..helper import format_result


def delete_lock(client, asset_id):
    result = client.execute('''
    mutation {
      deleteLocks(assetID: "%s") {
        id
      }
    }
    ''' % (asset_id))
    return format_result('deleteLocks', result)
