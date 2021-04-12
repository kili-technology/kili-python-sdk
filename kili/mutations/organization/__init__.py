import json
from typing import Optional

from typeguard import typechecked

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
    @typechecked
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
    @typechecked
    def update_properties_in_organization(self, organization_id: str, 
            name: Optional[str] = None, address: Optional[str] = None, 
            zip_code: Optional[str] = None, city: Optional[str] = None, 
            country: Optional[str] = None, license: Optional[dict] = None):
        """
        Modify an organization

        Parameters
        ----------
        - organization_id : str
        - name : str
        - address : str
        - license : dict
        - zip_code : str
        - city : str
        - country : str

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.
        """
        license_str = None if not license else json.dumps(license)
        variables = {
            'id': organization_id
        }
        if name is not None:
            variables['name'] = name
        if address is not None:
            variables['address'] = address
        if license_str is not None:
            variables['license'] = license_str
        if zip_code is not None:
            variables['zipCode'] = zip_code
        if city is not None:
            variables['city'] = city
        if country is not None:
            variables['country'] = country
        result = self.auth.client.execute(
            GQL_UPDATE_PROPERTIES_IN_ORGANIZATION, variables)
        return format_result('data', result)
