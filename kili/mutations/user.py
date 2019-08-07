from ..helper import format_result


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
    return format_result('signIn', result)


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
    return format_result('createUser', result)
