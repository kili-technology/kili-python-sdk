"""Tag use cases."""
from typing import Dict, List, Literal, Sequence

from kili.domain.project import ProjectId
from kili.domain.tag import TagId
from kili.gateways.kili_api_gateway import KiliAPIGateway
from kili.utils.tqdm import tqdm


class TagUseCases:
    """Tag use cases."""

    def __init__(self, kili_api_gateway: KiliAPIGateway) -> None:
        self._kili_api_gateway = kili_api_gateway

    def get_tags_of_organization(self, fields: Sequence[str]) -> List[Dict]:
        """Get tags of organization."""
        return self._kili_api_gateway.list_tags_by_org(fields=fields)

    def get_tags_of_project(self, project_id: str, fields: Sequence[str]) -> List[Dict]:
        """Get tags of project."""
        return self._kili_api_gateway.list_tags_by_project(
            project_id=ProjectId(project_id), fields=fields
        )

    def tag_project(
        self, project_id: str, tags: Sequence[str], disable_tqdm: bool
    ) -> List[Dict[Literal["id"], str]]:
        """Assign tags to a project."""
        tags_of_orga = self._kili_api_gateway.list_tags_by_org(fields=("id", "label"))
        tag_name_to_id = {tag["label"]: tag["id"] for tag in tags_of_orga}

        ret_tags = []
        for tag in tqdm(tags, desc="Tagging project", disable=disable_tqdm):
            # check if the provided tag is an id
            if tag in tag_name_to_id.values():
                tag_id = tag
            # check if the provided tag is a tag label
            elif tag in tag_name_to_id.keys():
                tag_id = tag_name_to_id[tag]
            else:
                raise ValueError(f"Tag {tag} not found in organization with tags: {tags_of_orga}")

            ret_tags.append(
                {
                    "id": self._kili_api_gateway.check_tag(
                        project_id=ProjectId(project_id), tag_id=TagId(tag_id)
                    )
                }
            )

        return ret_tags
