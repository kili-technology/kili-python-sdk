
def gql_user(fragment):
    return(f'''
query($where: UserWhere!, $first: PageSize!, $skip: Int!) {{
  data: users(where: $where, first: $first, skip: $skip) {{
    {fragment}
  }}
}}
''')
