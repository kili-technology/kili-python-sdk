def gql_locks(fragment):
    return(f'''
query($where: LockWhere!, $first: PageSize!, $skip: Int!) {{
  data: locks(where: $where, first: $first, skip: $skip) {{
    {fragment}
  }}
}}
''')
