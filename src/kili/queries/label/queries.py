"""
Queries of label queries
"""


def gql_labels(fragment):
    """
    Return the GraphQL labels query
    """
    return f"""
query ($where: LabelWhere!, $first: PageSize!, $skip: Int!) {{
  data: labels(where: $where, first: $first, skip: $skip) {{
    {fragment}
  }}
}}
"""


GQL_LABELS_COUNT = """
query($where: LabelWhere!) {
  data: countLabels(where: $where)
}
"""
