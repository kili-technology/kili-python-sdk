"""Tag use cases."""
from collections import defaultdict
from typing import Dict, List, Sequence

from kili.adapters.kili_api_gateway import KiliAPIGateway
from kili.domain.project import ProjectId
from kili.domain.tag import TagId
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
        self, project_id: str, tag_ids: Sequence[str], disable_tqdm: bool
    ) -> List[TagId]:
        """Assign tags to a project."""
        tags_of_orga = self._kili_api_gateway.list_tags_by_org(fields=("id",))
        tags_of_orga_ids = [tag["id"] for tag in tags_of_orga]

        ret_tags = []
        for tag_id in tqdm(tag_ids, desc="Tagging project", disable=disable_tqdm):
            if tag_id not in tags_of_orga_ids:
                raise ValueError(
                    f"Tag {tag_id} not found in organization with tag ids: {tags_of_orga}"
                )

            ret_tags.append(
                self._kili_api_gateway.check_tag(
                    project_id=ProjectId(project_id), tag_id=TagId(tag_id)
                )
            )

        return ret_tags

    def untag_project(
        self,
        project_id: str,
        tags: Optional[Sequence[str]],
        all: Optional[bool],  # pylint: disable=redefined-builtin
        disable_tqdm: bool,
    ) -> List[Dict[Literal["id"], str]]:
        """Remove tags from a project."""
        tags_of_project = self._kili_api_gateway.list_tags_by_project(
            project_id=ProjectId(project_id), fields=("label", "id")
        )
        tag_name_to_id = {tag["label"]: tag["id"] for tag in tags_of_project}

        tag_to_delete_ids = []
        if all:
            tag_to_delete_ids = [tag["id"] for tag in tags_of_project]
        else:
            assert tags
            for tag in tags:
                # check if the provided tag is an id
                if tag in tag_name_to_id.values():
                    tag_id = tag
                # check if the provided tag is a tag label
                elif tag in tag_name_to_id.keys():
                    tag_id = tag_name_to_id[tag]
                else:
                    raise ValueError(f"Tag {tag} not found in project with tags: {tags_of_project}")
                tag_to_delete_ids.append(tag_id)

        ret_tags: List[Dict[Literal["id"], str]] = [
            {
                "id": self._kili_api_gateway.uncheck_tag(
                    project_id=ProjectId(project_id), tag_id=TagId(tag_id)
                )
            }
            for tag_id in tqdm(tag_to_delete_ids, desc="Untagging project", disable=disable_tqdm)
        ]

        return ret_tags
    def get_tag_ids_from_labels(self, labels: Sequence[str]) -> List[TagId]:
        """Get tag ids from labels."""
        tags_of_orga = self._kili_api_gateway.list_tags_by_org(fields=("id", "label"))

        tag_label_to_id = defaultdict(list)
        for tag in tags_of_orga:
            tag_label_to_id[tag["label"]].append(tag["id"])

        tag_ids = []
        for label in labels:
            if label not in tag_label_to_id:
                raise ValueError(
                    f"Tag `{label}` not found in organization with tag ids: {tags_of_orga}"
                )
            if len(tag_label_to_id[label]) > 1:
                raise ValueError(
                    f"Several tags with ids ({tag_label_to_id[label]}) have the same label"
                    f" `{label}`. Please use tag ids instead."
                )
            tag_ids.append(TagId(tag_label_to_id[label][0]))

        return tag_ids
