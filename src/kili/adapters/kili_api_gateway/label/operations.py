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


def get_update_properties_in_label_mutation(fragment: str) -> str:
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


def get_append_many_labels_mutation(fragment: str) -> str:
    """Get the gql append many labels mutation."""
    return f"""
    mutation appendManyLabels($data: AppendManyLabelsData!, $where: AssetWhere!) {{
        data: appendManyLabels(data: $data, where: $where ) {{
            {fragment}
        }}
    }}
    """


def get_create_honeypot_mutation(fragment: str) -> str:
    """Get the gql create honeypot mutation."""
    return f"""
    mutation(
        $data: CreateHoneypotData!
        $where: AssetWhere!
    ) {{
    data: createHoneypot(
        data: $data
        where: $where
    ) {{
        {fragment}
    }}
    }}
    """


def get_append_to_labels_mutation(fragment: str) -> str:
    """Get the gql append to labels mutation."""
    return f"""
mutation(
    $data: AppendToLabelsData!
    $where: AssetWhere!
) {{
  data: appendToLabels(
    data: $data
    where: $where
  ) {{
      {fragment}
  }}
}}
"""
