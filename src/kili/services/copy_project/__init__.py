"""
Copy project implementation.
"""
from typing import Dict, Optional

from kili.authentication import KiliAuth
from kili.mutations.project import MutationsProject
from kili.queries.project import QueriesProject
from kili.queries.project_user import QueriesProjectUser


class CopyProject:  # pylint: disable=too-few-public-methods
    """
    Class for copying an existing project.
    """

    FIELDS_PROJECT = ["title", "jsonInterface", "inputType", "description", "id"]
    FIELDS_QUALITY_SETTINGS = [
        "consensusTotCoverage",
        "consensusMark",
        "minConsensusSize",
        "honeypotMark",
        "useHoneyPot",
        "reviewCoverage",
    ]

    def __init__(self, auth: KiliAuth) -> None:
        self.auth = auth

        mutations_project = MutationsProject(self.auth)
        queries_project = QueriesProject(self.auth)
        queries_project_user = QueriesProjectUser(self.auth)

        self.projects = queries_project.projects
        self.create_project = mutations_project.create_project
        self.append_to_roles = mutations_project.append_to_roles
        self.update_properties_in_project = mutations_project.update_properties_in_project
        self.project_users = queries_project_user.project_users

    def copy_project(  # pylint: disable=too-many-arguments
        self,
        from_project_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        copy_json_interface: bool = True,
        copy_quality_settings: bool = True,
        copy_members: bool = True,
    ) -> str:
        """Copy an existing project.

        Copy an existing source project from its ID.

        Args:
            from_project_id: Project ID to copy from.
            title: Title for the new project. Defaults to source project
                title if `None` is provided.
            description: Description for the new project. Defaults to empty string
                if `None` is provided.
            copy_json_interface: Copy the json interface from the source project to the new one.
            copy_quality_settings: Copy the quality settings from the source project to the new one.
            copy_members: Copy the members from the source project to the new one.

        Returns:
            The created project ID.

        Examples:
            >>> kili.copy_project(from_project_id="clbqn56b331234567890l41c0")
        """
        fields = self.FIELDS_PROJECT
        if copy_quality_settings:
            fields = fields + self.FIELDS_QUALITY_SETTINGS

        src_project = self.projects(  # type: ignore
            project_id=from_project_id,
            fields=fields,
        )[0]

        new_project_title = title
        if new_project_title is None:
            new_project_title = self._generate_project_title(src_title=src_project["title"])

        new_project_description = description
        if new_project_description is None:
            new_project_description = ""

        json_interface = {"jobs": {}}
        if copy_json_interface:
            json_interface = src_project["jsonInterface"]

        new_project_id = self.create_project(
            input_type=src_project["inputType"],
            json_interface=json_interface,
            title=new_project_title,
            description=new_project_description,
        )["id"]

        if copy_members:
            self._copy_members(from_project_id, new_project_id)

        if copy_quality_settings:
            self._copy_quality_settings(new_project_id, src_project)

        return new_project_id

    def _generate_project_title(self, src_title: str) -> str:
        projects = self.projects(fields=["title"])
        proj_titles = {proj["title"] for proj in projects}
        new_title = f"{src_title} (copy)"
        i = 1
        while new_title in proj_titles:
            new_title = f"{src_title} (copy {i})"
            i += 1
        return new_title

    def _copy_members(self, from_project_id: str, new_project_id: str) -> None:
        members = self.project_users(
            project_id=from_project_id,
            fields=["activated", "role", "user.email", "invitationStatus"],
        )
        members = [memb for memb in members if memb["invitationStatus"] != "DEFAULT_ACCEPTED"]
        members = [memb for memb in members if memb["activated"]]

        for m in members:
            self.append_to_roles(
                project_id=new_project_id,
                user_email=m["user"]["email"],
                role=m["role"],
            )

    def _copy_quality_settings(self, new_project_id: str, src_project: Dict) -> None:
        self.update_properties_in_project(
            project_id=new_project_id,
            consensus_mark=src_project["consensusMark"],
            consensus_tot_coverage=src_project["consensusTotCoverage"],
            honeypot_mark=src_project["honeypotMark"],
            min_consensus_size=src_project["minConsensusSize"],
            use_honeypot=src_project["useHoneyPot"],
            review_coverage=src_project["reviewCoverage"],
        )
