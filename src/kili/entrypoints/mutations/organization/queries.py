"""Queries of organization mutations."""

from .fragments import ORGANIZATION_FRAGMENT

GQL_CREATE_ORGANIZATION = f"""
mutation(
    $data: CreateOrganizationData!
) {{
  data: createOrganization(
    data: $data
  ) {{
    {ORGANIZATION_FRAGMENT}
  }}
}}
"""

GQL_UPDATE_PROPERTIES_IN_ORGANIZATION = f"""
mutation(
    $id: ID!
    $name: String
    $license: String
) {{
  data: updatePropertiesInOrganization(
    where: {{id: $id}}
    data: {{
      name: $name
      license: $license
    }}
  ) {{
    {ORGANIZATION_FRAGMENT}
  }}
}}
"""
