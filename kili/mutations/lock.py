from ..helper import format_result


def delete_lock(client, lock_id):
    result = client.execute('''
    mutation {
      deleteLock(lockID: "%s") {
        id
      }
    }
    ''' % (lock_id))
    return format_result('deleteLock', result)
