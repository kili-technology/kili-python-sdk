"""Client presentation methods for tags."""

from typing import Dict, List, Optional, Sequence

import requests
from typeguard import typechecked

from kili.gateways.kili_api_gateway import KiliAPIGateway
from kili.utils.logcontext import for_all_methods, log_call


@for_all_methods(log_call, exclude=["__init__"])
class TagClientMethods:
    """Methods attached to the Kili client, to run actions on tags."""

    kili_api_gateway: KiliAPIGateway
    http_client: requests.Session

    @typechecked
    def tags(
        self,
        *,
        project_id: Optional[str] = None,
        fields: Sequence[str] = ("id", "organizationId", "label", "checkedForProjects")
    ) -> List[Dict]:
        """Get tags.

        Args:
            organization_id: Id of the organization to which the tags belong.
            project_id: Id of the project to which the tags belong.
            fields: Fields to be retrieved.
                See the [documentation](https://docs.kili-technology.com/reference/graphql-api#tag)
                for all possible fields.

        Returns:
            A list of tags as dictionaries.
        """
        return (
            self.kili_api_gateway.list_tags_by_project(project_id=project_id, fields=fields)
            if project_id is not None
            else self.kili_api_gateway.list_tags_by_org(fields=fields)
        )

    @typechecked
    def tag_project(
        self,
        project_id: str,
        tags: Optional[Sequence[str]] = None,
        tag_ids: Optional[Sequence[str]] = None,
    ) -> List[Dict]:
        """Link a tag to a project.

        Args:
            project_id: Id of the project.
            tags: List of tags to associate to the project.
            tag_ids: List of tag ids to associate to the project. Used only if tags is None.

        Returns:
            A list of dictionary with the tag ids.
        """
        if tags is None and tag_ids is None:
            raise ValueError("Either `tags` or `tag_ids` must be provided.")
        if tags is not None and tag_ids is not None:
            raise ValueError("Only one of `tags` or `tag_ids` must be provided.")

        raise NotImplementedError
