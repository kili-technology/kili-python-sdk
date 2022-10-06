"""
Queries and organization queries
"""


def gql_organizations(fragment):
    """
    Return the GraphQL organizations query
    """
    return f"""
query($where: OrganizationWhere!, $first: PageSize!, $skip: Int!) {{
  data: organizations(where: $where, first: $first, skip: $skip) {{
    {fragment}
  }}
}}
"""


GQL_ORGANIZATIONS_COUNT = """
query($where: OrganizationWhere!) {
  data: countOrganizations(where: $where)
}
"""

GQL_ORGANIZATION_METRICS = """
query($where: OrganizationMetricsWhere!) {
  data: organizationMetrics(where: $where) {
    numberOfAnnotations
    numberOfHours
    numberOfLabeledAssets
  }
}
"""
