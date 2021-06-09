def gql_issues(fragment):
    return(f'''
query ($where: IssueWhere!, $first: PageSize!, $skip: Int!) {{
  data: issues(where: $where, first: $first, skip: $skip) {{
    {fragment}
  }}
}}
''')


GQL_LABELS_COUNT = f'''
query($where: IssueWhere!) {{
  data: countIssues(where: $where)
}}
'''
