"""
User mutations
"""

from typing import Optional

from typeguard import typechecked

from ...helpers import Compatible, format_result
from .queries import (GQL_CREATE_USER,
                      GQL_RESET_PASSWORD,
                      GQL_UPDATE_PASSWORD, GQL_UPDATE_PROPERTIES_IN_USER)


class MutationsUser:
    """
    Set of User mutations
    """
    # pylint: disable=too-many-arguments,too-many-locals

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
    def create_user(self,
                    email: str = None,
                    password: str = None,
                    organization_role: str = None,
                    firstname: Optional[str] = None,
                    lastname: Optional[str] = None):
        """
        Add a user to your organization.

        Parameters
        ----------
        - email : str
            Email of the new user, used as his unique identifier.
        - password : str
            On the first sign in, he will use this password and be able to change it.
        - organization_role : str
            One of "ADMIN", "USER".
        - firstname : str, optional (default = None)
            First name of the new user.
        - lastname : str, optional (default = None)
            Last name of the new user.

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.
        """
        variables = {
            'data': {'email': email,
                     'password': password,
                     'organizationRole': organization_role}
        }
        if firstname is not None:
            variables['data']['firstname'] = firstname
        if lastname is not None:
            variables['data']['lastname'] = lastname
        result = self.auth.client.execute(GQL_CREATE_USER, variables)
        return format_result('data', result)

    @Compatible(['v1', 'v2'])
    @typechecked
    def update_password(self, email: str, old_password: str, new_password_1: str,
                        new_password_2: str):
        """
        Allows you to modify the password you use to connect to Kili.
        This resolver only works for on-premise installations without Auth0.

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
            'data': {'oldPassword': old_password,
                     'newPassword1': new_password_1,
                     'newPassword2': new_password_2},
            'where': {'email': email}
        }
        result = self.auth.client.execute(GQL_UPDATE_PASSWORD, variables)
        return format_result('data', result)

    @Compatible(['v1', 'v2'])
    @typechecked
    def reset_password(self, email: str):
        """
        Reset password

        This resolver only works for on-premise installations without Auth0,
        if your organization allows Kili to send emails.

        Parameters
        ----------
        - email : str
            Email of the person whose password has to be reset.

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.
        """
        variables = {'where': {'email': email}}
        result = self.auth.client.execute(GQL_RESET_PASSWORD, variables)
        return format_result('data', result)

    @Compatible(['v1', 'v2'])
    @typechecked
    def update_properties_in_user(self,
                                  email: str,
                                  firstname: Optional[str] = None,
                                  lastname: Optional[str] = None,
                                  organization_id: Optional[str] = None,
                                  organization_role: Optional[str] = None,
                                  activated: Optional[bool] = None):
        """
        Update the properties of a user

        Parameters
        ----------
        - email : str
            The email is the identifier of the user.
        - firstname : str, optional (default = None)
            Change the first name of the user.
        - lastname : str, optional (default = None)
            Change the last name of the user.
        - organization_id : str, optional (default = None)
            Change the organization the user is related to.
        - organization_role : str, optional (default = None)
            Change the role of the user. One of "ADMIN", "TEAM_MANAGER", "REVIEWER", "LABELER".
        - activated : bool, optional (default = None)
            In case we want to deactivate a user, but keep it.

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.
        """
        variables = {
            'email': email,
        }
        if firstname is not None:
            variables['firstname'] = firstname
        if lastname is not None:
            variables['lastname'] = lastname
        if organization_id is not None:
            variables['organizationId'] = organization_id
        if organization_role is not None:
            variables['organizationRole'] = organization_role
        if activated is not None:
            variables['activated'] = activated
        result = self.auth.client.execute(
            GQL_UPDATE_PROPERTIES_IN_USER, variables)
        return format_result('data', result)
