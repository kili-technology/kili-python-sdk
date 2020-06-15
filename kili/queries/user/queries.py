def gql_users(fragment):
    return(f'''
query($where: UserWhere!, $first: PageSize!, $skip: Int!) {{
  data: users(where: $where, first: $first, skip: $skip) {{
    {fragment}
  }}
}}
''')
