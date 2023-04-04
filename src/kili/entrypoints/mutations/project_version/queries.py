"""Queries of project version mutations."""

from .fragments import PROJECT_VERSION_FRAGMENT

GQL_UPDATE_PROPERTIES_IN_PROJECT_VERSION = f"""
mutation(
    $id: ID!
    $content: String
) {{
  data: updatePropertiesInProjectVersion(
    where: {{id: $id}}
    data: {{
      content: $content
    }}
  ) {{
    {PROJECT_VERSION_FRAGMENT}
  }}
}}
"""
