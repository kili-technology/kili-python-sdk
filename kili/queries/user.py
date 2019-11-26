from ..helper import format_result


def get_user(client, email: str):
    result = client.execute('''
    query {
      getUser(email: "%s") {
        id
      }
    }
    ''' % (email))
    return format_result('getUser', result)
