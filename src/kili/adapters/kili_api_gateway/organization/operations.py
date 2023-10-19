"""Collection of Organization's related GraphQL queries and mutations."""

def get_create_organization_mutation(fragment: str) -> str:
    """Return the GraphQL createOrganization mutation."""
    return f"""
mutation(
    $data: CreateOrganizationData!
) {{
  data: createOrganization(
    data: $data
  ) {{
    {fragment}
  }}
}}
"""


def get_list_organizations_query(fragment: str) -> str:
    """Return the GraphQL organizations query."""
    return f"""
        query organizations($where: OrganizationWhere!, $first: PageSize!, $skip: Int!) {{
            data: organizations(where: $where, first: $first, skip: $skip) {{
                {fragment}
            }}
        }}
        """


COUNT_ORGANIZATIONS_QUERY = """
        query countOrganizations($where: OrganizationWhere!) {
        data: countOrganizations(where: $where)
        }
    """


GET_ORGANIZATION_METRICS_QUERY = """
    query organizationMetrics($where: OrganizationMetricsWhere!) {
        data: organizationMetrics(where: $where) {
            numberOfAnnotations
            numberOfHours
            numberOfLabeledAssets
        }
    }
    """


def get_update_properties_in_organization(fragment: str) -> str:
    """Return the GraphQL updatePropertiesInOrganization mutation."""
    return f"""
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
    {fragment}
  }}
}}
"""
