"""Project mutations."""

from typing import Dict, Literal, Optional

from typeguard import typechecked

from kili.entrypoints.base import BaseOperationEntrypointMixin
from kili.entrypoints.mutations.exceptions import MutationError
from kili.services.copy_project import ProjectCopier
from kili.utils.logcontext import for_all_methods, log_call

from .queries import (
    GQL_APPEND_TO_ROLES,
    GQL_DELETE_FROM_ROLES,
    GQL_PROJECT_DELETE_ASYNCHRONOUSLY,
    GQL_PROJECT_UPDATE_ANONYMIZATION,
    GQL_UPDATE_PROPERTIES_IN_PROJECT,
    GQL_UPDATE_PROPERTIES_IN_ROLE,
)


@for_all_methods(log_call, exclude=["__init__"])
class MutationsProject(BaseOperationEntrypointMixin):
    """Set of Project mutations."""

    @typechecked
    def append_to_roles(
        self,
        project_id: str,
        user_email: str,
        role: Literal["ADMIN", "TEAM_MANAGER", "REVIEWER", "LABELER"] = "LABELER",
    ) -> Dict:
        """Add a user to a project.

        !!! info
            If the user does not exist in your organization, he/she is invited and added
                both to your organization and project. This function can also be used to change
                the role of the user in the project.

        Args:
            project_id: Identifier of the project
            user_email: The email of the user.
                This email is used as the unique identifier of the user.
            role: The role of the user.

        Returns:
            A dictionary with the project user information.


        Examples:
            >>> kili.append_to_roles(project_id=project_id, user_email='john@doe.com')
        """
        variables = {
            "data": {"role": role, "userEmail": user_email},
            "where": {"id": project_id},
        }
        result = self.graphql_client.execute(GQL_APPEND_TO_ROLES, variables)

        project_data = self.format_result("data", result)
        for project_user in project_data["roles"]:
            if project_user["user"]["email"] == user_email.lower() and project_user["role"] == role:
                return project_user

        raise MutationError(
            f"Failed to mutate user {user_email} to role {role} for project {project_id}."
        )

    @typechecked
    def update_properties_in_role(
        self, role_id: str, project_id: str, user_id: str, role: str
    ) -> Dict:
        """Update properties of a role.

        !!! info
            To be able to change someone's role, you must be either of:

            - an admin of the project
            - a team manager of the project
            - an admin of the organization

        Args:
            role_id: Role identifier of the user. E.g. : 'to-be-deactivated'
            project_id: Identifier of the project
            user_id: The email or identifier of the user with updated role
            role: The new role.
                Possible choices are: `ADMIN`, `TEAM_MANAGER`, `REVIEWER`, `LABELER`

        Returns:
            A dictionary with the project user information.
        """
        variables = {
            "roleID": role_id,
            "projectID": project_id,
            "userID": user_id,
            "role": role,
        }
        result = self.graphql_client.execute(GQL_UPDATE_PROPERTIES_IN_ROLE, variables)
        return self.format_result("data", result)

    @typechecked
    def delete_from_roles(self, role_id: str) -> Dict[Literal["id"], str]:
        """Delete users by their role_id.

        Args:
            role_id: Identifier of the project user (not the ID of the user)

        Returns:
            A dict with the project id.
        """
        variables = {"where": {"id": role_id}}
        result = self.graphql_client.execute(GQL_DELETE_FROM_ROLES, variables)
        return self.format_result("data", result)

    @typechecked
    def delete_project(self, project_id: str) -> str:
        """Delete a project permanently.

        Args:
            project_id: Identifier of the project

        Returns:
            A string with the deleted project id.
        """
        variables = {"where": {"id": project_id}}
        result = self.graphql_client.execute(GQL_PROJECT_DELETE_ASYNCHRONOUSLY, variables)
        return self.format_result("data", result)

    @typechecked
    def archive_project(self, project_id: str) -> Dict[Literal["id"], str]:
        """Archive a project.

        Args:
            project_id: Identifier of the project.

        Returns:
            A dict with the id of the project.
        """
        variables = {
            "projectID": project_id,
            "archived": True,
        }

        result = self.graphql_client.execute(GQL_UPDATE_PROPERTIES_IN_PROJECT, variables)

        return self.format_result("data", result)

    @typechecked
    def unarchive_project(self, project_id: str) -> Dict[Literal["id"], str]:
        """Unarchive a project.

        Args:
            project_id: Identifier of the project

        Returns:
            A dict with the id of the project.
        """
        variables = {
            "projectID": project_id,
            "archived": False,
        }

        result = self.graphql_client.execute(GQL_UPDATE_PROPERTIES_IN_PROJECT, variables)
        return self.format_result("data", result)

    @typechecked
    def copy_project(  # pylint: disable=too-many-arguments
        self,
        from_project_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        copy_json_interface: bool = True,
        copy_quality_settings: bool = True,
        copy_members: bool = True,
        copy_assets: bool = False,
        copy_labels: bool = False,
        disable_tqdm: Optional[bool] = None,
    ) -> str:
        """Create new project from an existing project.

        Args:
            from_project_id: Project ID to copy from.
            title: Title for the new project. Defaults to source project
                title if `None` is provided.
            description: Description for the new project. Defaults to empty string
                if `None` is provided.
            copy_json_interface: Include json interface in the copy.
            copy_quality_settings: Include quality settings in the copy.
            copy_members: Include members in the copy.
            copy_assets: Include assets in the copy.
            copy_labels: Include labels in the copy.
            disable_tqdm: Disable tqdm progress bars.

        Returns:
            The created project ID.

        Examples:
            >>> kili.copy_project(from_project_id="clbqn56b331234567890l41c0")
        """
        return ProjectCopier(self).copy_project(  # pyright: ignore[reportGeneralTypeIssues]
            from_project_id,
            title,
            description,
            copy_json_interface,
            copy_quality_settings,
            copy_members,
            copy_assets,
            copy_labels,
            disable_tqdm,
        )

    @typechecked
    def update_project_anonymization(
        self, project_id: str, should_anonymize: bool = True
    ) -> Dict[Literal["id"], str]:
        """Anonymize the project for the labelers and reviewers.

        !!! info
            Compatible with versions of the Kili app >= 2.135.0

        Args:
            project_id: Identifier of the project
            should_anonymize: The value to be applied. Defaults to `True`.

        Returns:
            A dict with the id of the project which indicates if the mutation was successful,
                or an error message.

        Examples:
            >>> kili.update_project_anonymization(project_id=project_id)
            >>> kili.update_project_anonymization(project_id=project_id, should_anonymize=False)
        """
        variables = {
            "input": {
                "id": project_id,
                "shouldAnonymize": should_anonymize,
            }
        }

        result = self.graphql_client.execute(GQL_PROJECT_UPDATE_ANONYMIZATION, variables)
        return self.format_result("data", result)
