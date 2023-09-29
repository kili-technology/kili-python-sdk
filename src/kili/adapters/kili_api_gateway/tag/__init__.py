"""Mixin extending Kili API Gateway class with Tags related operations."""

from typing import Dict, List

from kili.adapters.kili_api_gateway.base import BaseOperationMixin
from kili.adapters.kili_api_gateway.helpers.queries import fragment_builder
from kili.domain.project import ProjectId
from kili.domain.tag import TagId
from kili.domain.types import ListOrTuple

from .operations import (
    GQL_CHECK_TAG,
    GQL_DELETE_TAG,
    GQL_UNCHECK_TAG,
    GQL_UPDATE_TAG,
    get_list_tags_by_org_query,
    get_list_tags_by_project_query,
)
from .types import UpdateTagReturnData


class TagOperationMixin(BaseOperationMixin):
    """GraphQL Mixin extending GraphQL Gateway class with Tags related operations."""

    def list_tags_by_org(self, fields: ListOrTuple[str]) -> List[Dict]:
        """Send a GraphQL request calling listTagsByOrg resolver."""
        fragment = fragment_builder(fields=fields)
        query = get_list_tags_by_org_query(fragment)
        result = self.graphql_client.execute(query)
        return result["data"]

    def list_tags_by_project(self, project_id: ProjectId, fields: ListOrTuple[str]) -> List[Dict]:
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

    def uncheck_tag(self, project_id: ProjectId, tag_id: TagId) -> TagId:
        """Send a GraphQL request calling uncheckTag resolver.

        WARNING: The resolved expects the tag to be checked for the project in the first place,
            do not call optimistically.
        """
        variables = {"projectId": project_id, "tagId": tag_id}
        result = self.graphql_client.execute(GQL_UNCHECK_TAG, variables)
        return TagId(result["data"]["id"])

    def update_tag(self, tag_id: TagId, label: str) -> UpdateTagReturnData:
        """Send a GraphQL request calling updateTag resolver."""
        variables = {"tagId": tag_id, "data": {"label": label}}
        result = self.graphql_client.execute(GQL_UPDATE_TAG, variables)
        return UpdateTagReturnData(
            affected_rows=result["data"]["affectedRows"],
            updated_tag_id=TagId(result["data"]["updatedTag"]["id"]),
        )

    def delete_tag(self, tag_id: TagId) -> bool:
        """Send a GraphQL request calling deleteTag resolver."""
        variables = {"tagId": tag_id}
        result = self.graphql_client.execute(GQL_DELETE_TAG, variables)
        return result["data"]
