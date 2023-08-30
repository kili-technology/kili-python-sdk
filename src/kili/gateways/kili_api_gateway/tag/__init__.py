"""Mixin extending Kili API Gateway class with Tags related operations."""

from typing import Dict, List, Sequence

from kili.core.graphql.graphql_client import GraphQLClient
from kili.core.graphql.utils import fragment_builder


class TagOperationMixin:
    """GraphQL Mixin extending GraphQL Gateway class with Tags related operations."""

    graphql_client: GraphQLClient

    def list_tags_by_org(self, fields: Sequence[str]) -> List[Dict]:
        """Send a GraphQL request calling listTagsByOrg resolver."""
        fragment = fragment_builder(fields=fields)
        query = f"""query listTagsByOrg {{
            data: listTagsByOrg {{
                {fragment}
            }}
        }}
        """
        result = self.graphql_client.execute(query=query)
        return result["data"]

    def list_tags_by_project(self, project_id: str, fields: Sequence[str]) -> List[Dict]:
        """Send a GraphQL request calling listTagsByProject resolver."""
        fragment = fragment_builder(fields=fields)
        query = f"""query listTagsByProject($projectId: ID!) {{
            data: listTagsByProject(projectId: $projectId) {{
                {fragment}
            }}
        }}
        """
        variables = {"projectId": project_id}
        result = self.graphql_client.execute(query, variables)
        return result["data"]
