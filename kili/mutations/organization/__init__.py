from ...helpers import Compatible, format_result
from .queries import (GQL_CREATE_ORGANIZATION,
                      GQL_UPDATE_PROPERTIES_IN_ORGANIZATION)


class MutationsOrganization:

    def __init__(self, auth):
        """
        Initializes the subclass

        Parameters
        ----------
        - auth : KiliAuth object
        """
        self.auth = auth

    @Compatible(['v1', 'v2'])
    def create_organization(self, name: str, address: str, zip_code: str, city: str, country: str):
        """
        Create an organization

        Each user must be linked to an organization

        Parameters
        ----------
        - name : str
        - address : str
        - zip_code : str
        - city : str
        - country : str

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.
        """
        variables = {
            'name': name,
            'address': address,
            'zipCode': zip_code,
            'city': city,
            'country': country
        }
        result = self.auth.client.execute(GQL_CREATE_ORGANIZATION, variables)
        return format_result('data', result)

    @Compatible(['v1', 'v2'])
    def update_properties_in_organization(self, organization_id: str, name: str, address: str, zip_code: str, city: str, country: str):
        """
        Modify an organization

        Parameters
        ----------
        - organization_id : str
        - name : str
        - address : str
        - zip_code : str
        - city : str
        - country : str

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.
        """
        variables = {
            'id': organization_id,
            'name': name,
            'address': address,
            'zipCode': zip_code,
            'city': city,
            'country': country
        }
        result = self.auth.client.execute(
            GQL_UPDATE_PROPERTIES_IN_ORGANIZATION, variables)
        return format_result('data', result)
