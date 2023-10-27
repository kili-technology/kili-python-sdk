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


def get_get_organization_metrics_query(fragment: str) -> str:
    """Return the GraphQL organizationMetrics query."""
    return f"""
    query organizationMetrics($where: OrganizationMetricsWhere!) {{
        data: organizationMetrics(where: $where) {{
            {fragment}
        }}
    }}
    """


def get_update_properties_in_organization_mutation(fragment: str) -> str:
    """Return the GraphQL updatePropertiesInOrganization mutation."""
    return f"""
mutation(
    $data: OrganizationData!,
    $where: OrganizationWhere!
) {{
  data: updatePropertiesInOrganization(
    data: $data
    where: $where,
  ) {{
    {fragment}
  }}
}}
"""
