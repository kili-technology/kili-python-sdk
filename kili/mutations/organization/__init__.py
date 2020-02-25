from ...helpers import format_result
from .queries import (GQL_CREATE_ORGANIZATION, GQL_DELETE_ORGANIZATION,
                      GQL_UPDATE_ORGANIZATION)


def create_organization(client, name: str, address: str, zip_code: str, city: str, country: str):
    variables = {
        'name': name,
        'address': address,
        'zipCode': zip_code,
        'city': city,
        'country': country
    }
    result = client.execute(GQL_CREATE_ORGANIZATION, variables)
    return format_result('data', result)


def update_organization(client, organization_id: str, name: str, address: str, zip_code: str, city: str, country: str):
    variables = {
        'organizationID': organization_id,
        'name': name,
        'address': address,
        'zipCode': zip_code,
        'city': city,
        'country': country
    }
    result = client.execute(GQL_UPDATE_ORGANIZATION, variables)
    return format_result('data', result)


def delete_organization(client, organization_id: str):
    variables = {'organizationID': organization_id}
    result = client.execute(GQL_DELETE_ORGANIZATION, variables)
    return format_result('data', result)
