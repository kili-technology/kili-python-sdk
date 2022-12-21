"""
Copy project implementation.
"""
from typing import Dict, Optional

from kili import mutations, queries
from kili.authentication import KiliAuth
from kili.exceptions import NotFound


class CopyProject:  # pylint: disable=too-few-public-methods
    """
    Class for copying an existing project.
    """

    FIELDS_PROJECT = ["title", "inputType", "description", "id"]
    FIELDS_JSON_INTERFACE = ["jsonInterface"]
    FIELDS_QUALITY_SETTINGS = [
        "consensusTotCoverage",
        "minConsensusSize",
        "useHoneyPot",
        "reviewCoverage",
    ]

    def __init__(self, auth: KiliAuth) -> None:
        self.auth = auth

        mutations_project = mutations.project.MutationsProject(self.auth)  # type: ignore
        queries_project = queries.project.QueriesProject(self.auth)  # type: ignore
        queries_project_user = queries.project_user.QueriesProjectUser(self.auth)  # type: ignore

        self.projects = queries_project.projects
        self.create_project = mutations_project.create_project
        self.append_to_roles = mutations_project.append_to_roles
        self.update_properties_in_project = mutations_project.update_properties_in_project
        self.project_users = queries_project_user.project_users

    def copy_project(  # pylint: disable=too-many-arguments
        self,
        from_project_id: str,
        title: Optional[str],
        description: Optional[str],
        copy_json_interface: bool,
        copy_quality_settings: bool,
        copy_members: bool,
    ) -> str:
        """
        Copy an existing project.
        """
        if not copy_json_interface and not copy_quality_settings and not copy_members:
            raise ValueError("At least one element has to be copied.")

        fields = self.FIELDS_PROJECT
        if copy_json_interface:
            fields += self.FIELDS_JSON_INTERFACE
        if copy_quality_settings:
            fields += self.FIELDS_QUALITY_SETTINGS

        src_project = self.projects(project_id=from_project_id, fields=fields)
        if len(src_project) == 0:
            raise NotFound(f"Cannot find project with id: {from_project_id}")
        src_project: Dict = src_project[0]

        new_project_title = title or self._generate_project_title(src_title=src_project["title"])

        new_project_description = description or ""

        json_interface = src_project["jsonInterface"] if copy_json_interface else {"jobs": {}}

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
        projects = self.projects(fields=["title"], search_query=f"{src_title}%")
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

        members = [
            memb
            for memb in members
            if memb["invitationStatus"] != "DEFAULT_ACCEPTED" and memb["activated"]
        ]

        for member in members:
            self.append_to_roles(
                project_id=new_project_id,
                user_email=member["user"]["email"],
                role=member["role"],
            )

    def _copy_quality_settings(self, new_project_id: str, src_project: Dict) -> None:
        self.update_properties_in_project(
            project_id=new_project_id,
            consensus_tot_coverage=src_project["consensusTotCoverage"],
            min_consensus_size=src_project["minConsensusSize"],
            use_honeypot=src_project["useHoneyPot"],
            review_coverage=src_project["reviewCoverage"],
        )
