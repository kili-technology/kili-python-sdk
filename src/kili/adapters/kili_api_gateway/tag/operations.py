"""GraphQL Tag operations."""

GQL_CHECK_TAG = """
mutation checkTag($data: CheckedTagData!) {
    data: checkTag(data: $data) {
        id
    }
}
"""

GQL_UNCHECK_TAG = """
mutation uncheckTag($projectId: ID!, $tagId: ID!) {
    data: uncheckTag(projectId: $projectId, tagId: $tagId) {
        id
    }
}
"""


def get_list_tags_by_org_query(fragment: str) -> str:
    """Return the GraphQL query to list tags by organization."""
    return f"""
    query listTagsByOrg {{
        data: listTagsByOrg {{
            {fragment}
        }}
    }}
    """


def get_list_tags_by_project_query(fragment: str) -> str:
    """Return the GraphQL query to list tags by project."""
    return f"""
    query listTagsByProject($projectId: ID!) {{
        data: listTagsByProject(projectId: $projectId) {{
            {fragment}
        }}
    }}
    """
