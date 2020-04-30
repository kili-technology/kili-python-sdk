from .fragments import ORGANIZATION_FRAGMENT

GQL_ORGANIZATIONS = f'''
query($where: OrganizationWhere!, $first: PageSize!, $skip: Int!) {{
  data: organizations(where: $where, first: $first, skip: $skip) {{
    {ORGANIZATION_FRAGMENT}
  }}
}}
'''
