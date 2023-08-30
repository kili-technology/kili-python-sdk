"""GraphQL Tags operations."""

GQL_CHECK_TAG = """
mutation checkTag($data: CheckedTagData!) {
    data: checkTag(data: $data) {
        id
    }
}
"""
