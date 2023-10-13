"""Collection of Organization's related GraphQL queries and mutations."""

ORGANIZATION_FRAGMENT = """
id
"""


def get_create_organization_mutation(fragment):
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


def get_list_organizations_query(fragment):
    """Return the GraphQL organizations query."""
    return f"""
        query organizations($where: OrganizationWhere!, $first: PageSize!, $skip: Int!) {{
            data: organizations(where: $where, first: $first, skip: $skip) {{
                {fragment}
            }}
        }}
        """


def get_count_organizations_query():
    """Return the GraphQL countOrganizations query."""
    return """
        query countOrganizations($where: OrganizationWhere!) {
        data: countOrganizations(where: $where)
        }
    """


def get_organization_metrics_query():
    """Return the GraphQL getOrganizationMetrics query."""
    return """
    query organizationMetrics($where: OrganizationMetricsWhere!) {
        data: organizationMetrics(where: $where) {
            numberOfAnnotations
            numberOfHours
            numberOfLabeledAssets
        }
    }
    """
