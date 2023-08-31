"""Mixin extending Kili API Gateway class with Tags related operations."""

from typing import Dict, List, Sequence

from kili.core.graphql.graphql_client import GraphQLClient
from kili.domain.tag import Tag
from kili.gateways.kili_api_gateway.queries import fragment_builder

from .operations import GQL_CHECK_TAG


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

    def check_tag(self, project_id: str, tag_id: str) -> Tag:
        """Send a GraphQL request calling checkTag resolver."""
        variables = {"data": {"tagId": tag_id, "projectId": project_id}}
        result = self.graphql_client.execute(GQL_CHECK_TAG, variables)
        return Tag(id_=result["data"]["id"])
