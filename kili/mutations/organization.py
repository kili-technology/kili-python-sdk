from ..helper import format_result


def create_organization(client, name: str, address: str, zip_code: str, city: str, country: str):
    result = client.execute('''
    mutation {
      createOrganization(name: "%s",
      address: "%s",
      zipCode: "%s",
      city: "%s",
      country: "%s") {
        id
      }
    }
    ''' % (name, address, zip_code, city, country))
    return format_result('createOrganization', result)


def update_organization(client, organization_id: str, name: str, address: str, zip_code: str, city: str, country: str):
    result = client.execute('''
    mutation {
      updateOrganization(organizationID: "%s",
      name: "%s",
      address: "%s",
      zipCode: "%s",
      city: "%s",
      country: "%s") {
        id
      }
    }
    ''' % (organization_id, name, address, zip_code, city, country))
    return format_result('updateOrganization', result)


def delete_organization(client, organization_id: str):
    result = client.execute('''
    mutation {
      deleteOrganization(organizationID: "%s") {
        id
      }
    }
    ''' % (organization_id))
    return format_result('deleteOrganization', result)
