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


def create_user_from_email_if_not_exists(client, name, email, organization_name, organization_role, project_id):
    result = client.execute('''
    mutation {
      createUserFromEmailIfNotExists(name: "%s",
      email: "%s",
      organizationName: "%s",
      organizationRole: %s,
      projectID: "%s") {
        id
      }
    }
    ''' % (name, email, organization_name, organization_role, project_id))
    return format_result('createUserFromEmailIfNotExists', result)


def update_user(client, user_id, name, email, phone, organization_id, organization_role):
    result = client.execute('''
    mutation {
      updateUser(userID: "%s",
      name: "%s",
      email: "%s",
      phone: "%s",
      organizationID: "%s",
      organizationRole: %s) {
        id
      }
    }
    ''' % (user_id, name, email, phone, organization_id, organization_role))
    return format_result('updateUser', result)


def update_password(client, email, old_password, new_password_1, new_password_2):
    result = client.execute('''
    mutation {
      updatePassword(email: "%s",
      oldPassword: "%s",
      newPassword1: "%s",
      newPassword2: "%s") {
        id
      }
    }
    ''' % (email, old_password, new_password_1, new_password_2))
    return format_result('updatePassword', result)


def reset_password(client, email):
    result = client.execute('''
    mutation {
      resetPassword(email: "%s") {
        id
      }
    }
    ''' % email)
    return format_result('resetPassword', result)
