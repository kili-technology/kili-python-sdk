"""GraphQL label operations."""

def get_labels_query(fragment: str) -> str:
    """Get the gql labels query."""
    return f"""
    query labels($where: LabelWhere!, $first: PageSize!, $skip: Int!) {{
        data: labels(where: $where, first: $first, skip: $skip) {{
            {fragment}
        }}
    }}
    """


GQL_COUNT_LABELS = """
query countLabels($where: LabelWhere!) {
    data: countLabels(where: $where)
}
"""
