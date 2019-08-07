from json import loads


def signin(client, email, password):
    result = client.execute('''
    mutation {
      signIn(email: "%s", password: "%s") {
        id
        token
        user {
          id
        }
      }
    }
    ''' % (email, password))
    return loads(result)['data']['signIn']


def create_user(client, name, email, password, phone, organization_id, organization_role):
    result = client.execute('''
    mutation {
      createUser(name: "%s",
      email: "%s",
      password: "%s",
      phone: "%s",
      organizationID: "%s",
      organizationRole: %s) {
        id
      }
    }
    ''' % (name, email, password, phone, organization_id, organization_role))
    return loads(result)['data']['createUser']
