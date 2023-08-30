"""Client presentation methods for tags."""

from typing import Dict, List, Literal, Optional, Sequence

import requests
from typeguard import typechecked

from kili.gateways.kili_api_gateway import KiliAPIGateway
from kili.utils.logcontext import for_all_methods, log_call
from kili.utils.tqdm import tqdm


@for_all_methods(log_call, exclude=["__init__"])
class TagClientMethods:
    """Methods attached to the Kili client, to run actions on tags."""

    kili_api_gateway: KiliAPIGateway
    http_client: requests.Session

    @typechecked
    def tags(
        self,
        project_id: Optional[str] = None,
        fields: Sequence[str] = ("id", "organizationId", "label", "checkedForProjects"),
    ) -> List[Dict]:
        """Get tags.

        Args:
            project_id: Id of the project to which the tags belong.
                If not provided, tags of the organization are retrieved.
            fields: Fields of tags to be retrieved.
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
    def tag_project(self, project_id: str, tags: Sequence[str]) -> List[Dict[Literal["id"], str]]:
        """Link tags to a project.

        Args:
            project_id: Id of the project.
            tags: Sequence of tags to associate to the project.
                The value of each tag can be its name or its id.

        Returns:
            A list of dictionary with the tag ids.
        """
        tags_of_orga = self.kili_api_gateway.list_tags_by_org(fields=("id", "label"))
        tag_name_to_id = {tag["label"]: tag["id"] for tag in tags_of_orga}

        ret_tags = []
        for tag in tqdm(tags, desc="Tagging project"):
            if tag in tag_name_to_id.values():
                tag_id = tag
            elif tag in tag_name_to_id.keys():
                tag_id = tag_name_to_id[tag]
            else:
                raise ValueError(f"Tag {tag} not found in project {project_id}")

            ret_tags.append(
                {"id": self.kili_api_gateway.check_tag(project_id=project_id, tag_id=tag_id).id_}
            )

        return ret_tags
