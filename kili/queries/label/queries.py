def gql_labels(fragment):
    return(f'''
query ($where: LabelWhere!, $first: PageSize!, $skip: Int!) {{
  data: labels(where: $where, first: $first, skip: $skip) {{
    {fragment}
  }}
}}
''')
