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
        tag_ids: Sequence[str],
        disable_tqdm: bool,
    ) -> List[TagId]:
        """Remove tags from a project."""
        tag_ids_of_project = {
            tag["id"]
            for tag in self._kili_api_gateway.list_tags_by_project(
                project_id=ProjectId(project_id), fields=("id",)
            )
        }

        for tag in tag_ids:
            if tag not in tag_ids_of_project:
                raise ValueError(
                    f"Tag {tag} not found in project with tag ids: {tag_ids_of_project}"
                )

        return [
            self._kili_api_gateway.uncheck_tag(
                project_id=ProjectId(project_id), tag_id=TagId(tag_id)
            )
            for tag_id in tqdm(tag_ids, desc="Untagging project", disable=disable_tqdm)
        ]

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
