from ...helpers import format_result
from .queries import (GQL_CREATE_USER,
                      GQL_CREATE_USER_FROM_EMAIL_IF_NOT_EXISTS,
                      GQL_RESET_PASSWORD, GQL_SIGN_IN, GQL_UPDATE_PASSWORD,
                      GQL_UPDATE_PROPERTIES_IN_USER, GQL_UPDATE_USER)


def signin(client, email: str, password: str):
    variables = {'email': email, 'password': password}
    result = client.execute(GQL_SIGN_IN, variables)
    return format_result('data', result)


def create_user(client, name: str, email: str, password: str, phone: str, organization_role: str):
    variables = {
        'name': name,
        'email': email,
        'password': password,
        'phone': phone,
        'organizationRole': organization_role
    }
    result = client.execute(GQL_CREATE_USER, variables)
    return format_result('data', result)


def create_user_from_email_if_not_exists(client, name: str, email: str, organization_role: str, project_id: str):
    variables = {
        'name': name,
        'email': email,
        'organizationRole': organization_role,
        'projectID': project_id
    }
    result = client.execute(
        GQL_CREATE_USER_FROM_EMAIL_IF_NOT_EXISTS, variables)
    return format_result('data', result)


def update_user(client, user_id: str, name: str, email: str, phone: str, organization_role: str):
    variables = {
        'userID': user_id,
        'name': name,
        'email': email,
        'phone': phone,
        'organizationRole': organization_role
    }
    result = client.execute(GQL_UPDATE_USER, variables)
    return format_result('data', result)


def update_password(client, email: str, old_password: str, new_password_1: str, new_password_2: str):
    variables = {
        'email': email,
        'oldPassword': old_password,
        'newPassword1': new_password_1,
        'newPassword2': new_password_2
    }
    result = client.execute(GQL_UPDATE_PASSWORD, variables)
    return format_result('data', result)


def reset_password(client, email: str):
    variables = {'email': email}
    result = client.execute(GQL_RESET_PASSWORD, variables)
    return format_result('data', result)


def update_properties_in_user(client, email: str, name: str = None, organization_id: str = None, organization_role: str = None, activated: bool = None):
    variables = {
        'email': email,
        'name': name,
        'organizationId': organization_id,
        'organizationRole': organization_role,
        'activated': activated
    }
    result = client.execute(GQL_UPDATE_PROPERTIES_IN_USER, variables)
    return format_result('data', result)
