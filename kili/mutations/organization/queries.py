from .fragments import ORGANIZATION_FRAGMENT

GQL_CREATE_ORGANIZATION = f'''
mutation(
    $name: String!
    $address: String!
    $zipCode: String!
    $city: String!
    $country: String!
) {{
  data: createOrganization(
    name: $name
    address: $address
    zipCode: $zipCode
    city: $city
    country: $country
  ) {{
    {ORGANIZATION_FRAGMENT}
  }}
}}
'''

GQL_UPDATE_PROPERTIES_IN_ORGANIZATION = f'''
mutation(
    $id: ID!
    $name: String
    $address: String
    $license: String
    $zipCode: String
    $city: String
    $country: String
) {{
  data: updatePropertiesInOrganization(
    where: {{id: $id}}
    data: {{
      name: $name
      address: $address
      license: $license
      zipCode: $zipCode
      city: $city
      country: $country
    }}
  ) {{
    {ORGANIZATION_FRAGMENT}
  }}
}}
'''
