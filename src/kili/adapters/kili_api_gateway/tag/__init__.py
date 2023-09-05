"""Mixin extending Kili API Gateway class with Tags related operations."""

from typing import Dict, List, Sequence

from kili.adapters.kili_api_gateway.queries import fragment_builder
from kili.domain.project import ProjectId
from kili.domain.tag import TagId

from ..base import BaseOperationMixin
from .operations import (
    GQL_CHECK_TAG,
    get_list_tags_by_org_query,
    get_list_tags_by_project_query,
)


class TagOperationMixin(BaseOperationMixin):
    """GraphQL Mixin extending GraphQL Gateway class with Tags related operations."""

    def list_tags_by_org(self, fields: Sequence[str]) -> List[Dict]:
        """Send a GraphQL request calling listTagsByOrg resolver."""
        fragment = fragment_builder(fields=fields)
        query = get_list_tags_by_org_query(fragment)
        result = self.graphql_client.execute(query)
        return result["data"]

    def list_tags_by_project(self, project_id: ProjectId, fields: Sequence[str]) -> List[Dict]:
        """Send a GraphQL request calling listTagsByProject resolver."""
        fragment = fragment_builder(fields=fields)
        query = get_list_tags_by_project_query(fragment)
        variables = {"projectId": project_id}
        result = self.graphql_client.execute(query, variables)
        return result["data"]

    def check_tag(self, project_id: ProjectId, tag_id: TagId) -> TagId:
        """Send a GraphQL request calling checkTag resolver."""
        variables = {"data": {"tagId": tag_id, "projectId": project_id}}
        result = self.graphql_client.execute(GQL_CHECK_TAG, variables)
        return TagId(result["data"]["id"])
