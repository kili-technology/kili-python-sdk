def get_user(client, email):
    result = client.execute('''
    query {
      getUser(email: "%s") {
        id
      }
    }
    ''' % (email))
    return loads(result)['data']['getUser']