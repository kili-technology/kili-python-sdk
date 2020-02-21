from ..helpers import format_result


def signin(client, email: str, password: str):
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


def create_user(client, name: str, email: str, password: str, phone: str, organization_role: str):
    result = client.execute('''
    mutation {
      createUser(name: "%s",
      email: "%s",
      password: "%s",
      phone: "%s",
      organizationRole: %s) {
        id
      }
    }
    ''' % (name, email, password, phone, organization_role))
    return format_result('createUser', result)


def create_user_from_email_if_not_exists(client, name: str, email: str, organization_role: str, project_id: str):
    result = client.execute('''
    mutation {
      createUserFromEmailIfNotExists(name: "%s",
      email: "%s",
      organizationRole: %s,
      projectID: "%s") {
        id
      }
    }
    ''' % (name, email, organization_role, project_id))
    return format_result('createUserFromEmailIfNotExists', result)


def update_user(client, user_id: str, name: str, email: str, phone: str, organization_role: str):
    result = client.execute('''
    mutation {
      updateUser(userID: "%s",
      name: "%s",
      email: "%s",
      phone: "%s",
      organizationRole: %s) {
        id
      }
    }
    ''' % (user_id, name, email, phone, organization_role))
    return format_result('updateUser', result)


def update_password(client, email: str, old_password: str, new_password_1: str, new_password_2: str):
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


def reset_password(client, email: str):
    result = client.execute('''
    mutation {
      resetPassword(email: "%s") {
        id
      }
    }
    ''' % email)
    return format_result('resetPassword', result)


def update_properties_in_user(client, email: str, name: str = None, organization_id: str = None, organization_role: str = None, activated: bool = None):
    formatted_name = 'null' if name is None else f'"{name}"'
    formatted_organization_id = 'null' if organization_id is None else f'"{organization_id}"'
    formatted_organization_role = 'null' if organization_role is None else f'"{organization_role}"'
    formatted_activated = 'null' if activated is None else str(
        activated).lower()

    result = client.execute('''
        mutation {
          updatePropertiesInUser(
            where: {email: "%s"},
            data: {
              name: %s
              organizationId: %s
              organizationRole: %s
              activated: %s
            }
          ) {
            id
          }
        }
        ''' % (email, formatted_name, formatted_organization_id, formatted_organization_role, formatted_activated))
    return format_result('updatePropertiesInUser', result)
