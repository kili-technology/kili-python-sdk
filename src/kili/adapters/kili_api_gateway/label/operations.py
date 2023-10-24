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


def get_update_properties_in_label_query(fragment: str) -> str:
    """Get the gql update properties in label query."""
    return f"""
    mutation(
        $where: LabelWhere!
        $data: LabelData!
    ) {{
    data: updatePropertiesInLabel(
        where: $where
        data:  $data
    ) {{
        {fragment}
    }}
    }}
    """


GQL_DELETE_LABELS = """
mutation($ids: [ID!]!) {
  data: deleteLabels(ids: $ids)
}
"""
