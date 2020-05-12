
def gql_organizations(fragment):
    return(f'''
query($where: OrganizationWhere!, $first: PageSize!, $skip: Int!) {{
  data: organizations(where: $where, first: $first, skip: $skip) {{
    {fragment}
  }}
}}
''')
