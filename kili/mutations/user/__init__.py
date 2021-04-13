from typing import Optional

from typeguard import typechecked

from ...helpers import Compatible, deprecate, format_result
from .queries import (GQL_CREATE_USER,
                      GQL_CREATE_USER_FROM_EMAIL_IF_NOT_EXISTS,
                      GQL_RESET_PASSWORD, GQL_SIGN_IN, GQL_UPDATE_API_KEY,
                      GQL_UPDATE_PASSWORD, GQL_UPDATE_PROPERTIES_IN_USER)


class MutationsUser:

    def __init__(self, auth):
        """
        Initializes the subclass

        Parameters
        ----------
        - auth : KiliAuth object
        """
        self.auth = auth

    @Compatible(['v1', 'v2'])
    @typechecked
    def create_user(self, name: str, email: str, password: str, organization_role: str):
        """
        Add a user to your organization.

        Parameters
        ----------
        - name : str
            Name of the new user.
        - email : str
            Email of the new user, used as his unique identifier.
        - password : str
            On the first sign in, he will use this password and be able to change it.
        - organization_role : str
            One of "ADMIN", "USER".

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.
        """
        variables = {
            'name': name,
            'email': email,
            'password': password,
            'organizationRole': organization_role
        }
        result = self.auth.client.execute(GQL_CREATE_USER, variables)
        return format_result('data', result)

    @Compatible(['v1', 'v2'])
    @typechecked
    def update_api_key(self, email: str, new_api_key: str):
        """
        Update API key

        Allows you to modify the API key you use to connect to Kili. This method is currently only active for Kili administrators.

        Parameters
        ----------
        - email : str
        - new_api_key : str

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.
        """
        variables = {
            'email': email,
            'newApiKey': new_api_key,
        }
        result = self.auth.client.execute(GQL_UPDATE_API_KEY, variables)
        return format_result('data', result)

    @Compatible(['v1', 'v2'])
    @typechecked
    def update_password(self, email: str, old_password: str, new_password_1: str, 
            new_password_2: str):
        """
        Allows you to modify the password you use to connect to Kili. This resolver only works for on-premise installations without Auth0.

        Parameters
        ----------
        - email : str
        - old_password : str
        - new_password_1 : str
            The new password.
        - new_password_2 : str
            A confirmation field for the new password.

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.
        """
        variables = {
            'email': email,
            'oldPassword': old_password,
            'newPassword1': new_password_1,
            'newPassword2': new_password_2
        }
        result = self.auth.client.execute(GQL_UPDATE_PASSWORD, variables)
        return format_result('data', result)

    @Compatible(['v1', 'v2'])
    @typechecked
    def reset_password(self, email: str):
        """
        Reset password

        This resolver only works for on-premise installations without Auth0, if your organization allows Kili to send emails.

        Parameters
        ----------
        - email : str
            Email of the person whose password has to be reset.

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.
        """
        variables = {'email': email}
        result = self.auth.client.execute(GQL_RESET_PASSWORD, variables)
        return format_result('data', result)

    @Compatible(['v1', 'v2'])
    @typechecked
    def update_properties_in_user(self, email: str, name: Optional[str] = None, 
            organization_id: Optional[str] = None, organization_role: Optional[str] = None, 
            activated: Optional[bool] = None):
        """
        Update the properties of a user

        Parameters
        ----------
        - email : str
            The email is the identifier of the user
        - name : str, optional (default = None)
        - organization_id : str, optional (default = None)
            Change the organization the user is related to.
        - organization_role : str, optional (default = None)
            Change the role of the user. One of "ADMIN", "REVIEWER", "LABELER", "READER".
        - activated : bool, optional (default = None)
            In case we want to deactivate a user, but keep it.

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.
        """
        variables = {
            'email': email,
        }
        if name is not None:
            variables['name'] = name
        if organization_id is not None:
            variables['organizationId'] = organization_id
        if organization_role is not None:
            variables['organizationRole'] = organization_role
        if activated is not None:
            variables['activated'] = activated
        result = self.auth.client.execute(
            GQL_UPDATE_PROPERTIES_IN_USER, variables)
        return format_result('data', result)
