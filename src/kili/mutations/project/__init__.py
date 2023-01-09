"""Project mutations."""

from json import dumps
from typing import Any, Dict, Optional, Union

from typeguard import typechecked

from kili import services

from ...authentication import KiliAuth
from ...helpers import format_result
from ...services.copy_project import ProjectCopier
from .helpers import verify_argument_ranges
from .queries import (
    GQL_APPEND_TO_ROLES,
    GQL_CREATE_PROJECT,
    GQL_DELETE_FROM_ROLES,
    GQL_DELETE_PROJECT,
    GQL_PROJECT_DELETE_ASYNCHRONOUSLY,
    GQL_UPDATE_PROPERTIES_IN_PROJECT,
    GQL_UPDATE_PROPERTIES_IN_ROLE,
)


class MutationsProject:
    """Set of Project mutations."""

    # pylint: disable=too-many-arguments,too-many-locals

    def __init__(self, auth: KiliAuth):
        """Initialize the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    @typechecked
    def append_to_roles(
        self, project_id: str, user_email: str, role: str = "LABELER"
    ) -> Dict[str, Union[str, dict, list, None]]:
        """Add a user to a project.

        !!! info
            If the user does not exist in your organization, he/she is invited and added
                both to your organization and project. This function can also be used to change
                the role of the user in the project.

        Args:
            project_id: Identifier of the project
            user_email: The email of the user.
                This email is used as the unique identifier of the user.
            role: One of {"ADMIN", "TEAM_MANAGER", "REVIEWER", "LABELER"}.

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.


        Examples:
            >>> kili.append_to_roles(project_id=project_id, user_email='john@doe.com')
        """
        variables = {
            "data": {"role": role, "userEmail": user_email},
            "where": {"id": project_id},
        }
        result = self.auth.client.execute(GQL_APPEND_TO_ROLES, variables)
        return format_result("data", result)

    @typechecked
    def update_properties_in_project(
        self,
        project_id: str,
        can_navigate_between_assets: Optional[bool] = None,
        can_skip_asset: Optional[bool] = None,
        consensus_mark: Optional[float] = None,
        consensus_tot_coverage: Optional[int] = None,
        description: Optional[str] = None,
        honeypot_mark: Optional[float] = None,
        instructions: Optional[str] = None,
        input_type: Optional[str] = None,
        json_interface: Optional[dict] = None,
        min_consensus_size: Optional[int] = None,
        number_of_assets: Optional[int] = None,
        number_of_skipped_assets: Optional[int] = None,
        number_of_remaining_assets: Optional[int] = None,
        number_of_reviewed_assets: Optional[int] = None,
        review_coverage: Optional[int] = None,
        should_relaunch_kpi_computation: Optional[bool] = None,
        title: Optional[str] = None,
        use_honeypot: Optional[bool] = None,
        metadata_types: Optional[dict] = None,
    ) -> Dict[str, Any]:
        """Update properties of a project.

        Args:
            project_id: Identifier of the project.
            can_navigate_between_assets:
                Activate / Deactivate the use of next and previous buttons in labeling interface.
            can_skip_asset: Activate / Deactivate the use of skip button in labeling interface.
            consensus_mark: Should be between 0 and 1.
            consensus_tot_coverage: Should be between 0 and 100.
                It is the percentage of the dataset that will be annotated several times.
            description : Description of the project.
            honeypot_mark : Should be between 0 and 1
            instructions : Instructions of the project.
            input_type: Currently, one of `AUDIO`, `IMAGE`, `PDF`, `TEXT`,
                `VIDEO`, `VIDEO_LEGACY`.
            json_interface: The json parameters of the project, see Edit your interface.
            min_consensus_size: Should be between 1 and 10
                Number of people that will annotate the same asset, for consensus computation.
            number_of_assets: Defaults to 0
            number_of_skipped_assets: Defaults to 0
            number_of_remaining_assets: Defaults to 0
            number_of_reviewed_assets: Defaults to 0
            review_coverage: Allow to set the percentage of assets
                that will be queued in the review interface.
                Should be between 0 and 100
            should_relaunch_kpi_computation: Technical field, added to indicate changes
                in honeypot or consensus settings
            title: Title of the project
            use_honeypot: Activate / Deactivate the use of honeypot in the project
            metadata_types: Types of the project metadata.
                Should be a `dict` of metadata fields name as keys and metadata types as values.
                Currently, possible types are: `string`, `number`

        Returns:
            A dict with the changed properties which indicates if the mutation was successful,
                else an error message.

        Examples:
            >>> kili.update_properties_in_project(project_id=project_id, title='New title')

        !!! example "Change Metadata Types"
            Metadata fields are by default interpreted as `string` types. To change the type
            of a metadata field, you can use the `update_properties_in_project` function with the
            metadata_types argument. `metadata_types` is given as a dict of metadata field names
            as keys and metadata types as values.
            Example:
            ```
            kili.update_properties_in_project(
                project_id = project_id,
                metadata_types = {
                    'customConsensus': 'number',
                    'sensitiveData': 'string',
                    'uploadedFromCloud': 'string',
                    'modelLabelErrorScore': 'number'
                }
            )
            ```
            Not providing a type for a metadata field or providing an unsupported one
            will default to the `string` type.
        """
        verify_argument_ranges(consensus_tot_coverage, min_consensus_size, review_coverage)

        variables = {
            "canNavigateBetweenAssets": can_navigate_between_assets,
            "canSkipAsset": can_skip_asset,
            "consensusMark": consensus_mark,
            "consensusTotCoverage": consensus_tot_coverage,
            "description": description,
            "honeypotMark": honeypot_mark,
            "instructions": instructions,
            "inputType": input_type,
            "jsonInterface": dumps(json_interface) if json_interface is not None else None,
            "metadataTypes": metadata_types,
            "minConsensusSize": min_consensus_size,
            "numberOfAssets": number_of_assets,
            "numberOfSkippedAssets": number_of_skipped_assets,
            "numberOfRemainingAssets": number_of_remaining_assets,
            "numberOfReviewedAssets": number_of_reviewed_assets,
            "projectID": project_id,
            "reviewCoverage": review_coverage,
            "shouldRelaunchKpiComputation": should_relaunch_kpi_computation,
            "title": title,
            "useHoneyPot": use_honeypot,
        }
        result = self.auth.client.execute(GQL_UPDATE_PROPERTIES_IN_PROJECT, variables)
        result = format_result("data", result)

        variables.pop("projectID")
        variables = {k: v for k, v in variables.items() if v is not None}

        new_project_settings = services.get_project(self, project_id, list(variables.keys()))

        result = {**result, **new_project_settings}
        return result

    @typechecked
    def create_project(
        self,
        input_type: str,
        json_interface: dict,
        title: str,
        description: str = "",
        project_type: Optional[str] = None,
    ) -> Dict:
        # pylint: disable=line-too-long
        """Create a project.

        Args:
            input_type: Currently, one of {AUDIO, IMAGE, PDF, TEXT, URL, VIDEO, VIDEO_LEGACY, NA}
            json_interface: The json parameters of the project, see Edit your interface.
            title: Title of the project
            description: Description of the project
            project_type:
                Currently, one of {
                    `IMAGE_CLASSIFICATION_SINGLE`,
                    `IMAGE_CLASSIFICATION_MULTI`,
                    `IMAGE_OBJECT_DETECTION_RECTANGLE`,
                    `IMAGE_OBJECT_DETECTION_POLYGON`,
                    `IMAGE_OBJECT_DETECTION_SEMANTIC`,
                    `OCR, PDF_CLASSIFICATION_SINGLE`,
                    `PDF_CLASSIFICATION_MULTI`,
                    `TEXT_CLASSIFICATION_SINGLE`,
                    `TEXT_CLASSIFICATION_MULTI`,
                    `TEXT_TRANSCRIPTION, TEXT_NER`,
                    `VIDEO_CLASSIFICATION_SINGLE`,
                    `VIDEO_FRAME_CLASSIFICATION`,
                    `VIDEO_FRAME_OBJECT_TRACKING`,
                    `SPEECH_TO_TEXT`
                }

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.

        Examples:
            >>> kili.create_project(input_type='IMAGE', json_interface=json_interface, title='Example')

        !!! example "Recipe"
            For more detailed examples on how to create projects,
                see [the recipe](https://docs.kili-technology.com/recipes/creating-a-project).
        """
        variables = {
            "data": {
                "description": description,
                "inputType": input_type,
                "jsonInterface": dumps(json_interface),
                "projectType": project_type,
                "title": title,
            }
        }
        result = self.auth.client.execute(GQL_CREATE_PROJECT, variables)
        return format_result("data", result)

    @typechecked
    def update_properties_in_role(self, role_id: str, project_id: str, user_id: str, role: str):
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
            A result object which indicates if the mutation was successful,
                or an error message.
        """
        variables = {
            "roleID": role_id,
            "projectID": project_id,
            "userID": user_id,
            "role": role,
        }
        result = self.auth.client.execute(GQL_UPDATE_PROPERTIES_IN_ROLE, variables)
        return format_result("data", result)

    @typechecked
    def delete_from_roles(self, role_id: str):
        """Delete users by their role_id.

        Args:
            role_id: Identifier of the project user (not the ID of the user)

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.
        """
        variables = {"where": {"id": role_id}}
        result = self.auth.client.execute(GQL_DELETE_FROM_ROLES, variables)
        return format_result("data", result)

    @typechecked
    def internal_delete_project(self, project_id: str):
        """Delete project permanently.
        WARNING: This resolver is for internal use by Kili Technology only.

        Args:
            project_id: Identifier of the project

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.
        """
        variables = {"projectID": project_id}
        result = self.auth.client.execute(GQL_DELETE_PROJECT, variables)
        return format_result("data", result)

    @typechecked
    def delete_project(self, project_id: str) -> str:
        """
        Delete a project permanently.

        Args:
            project_id: Identifier of the project

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.
        """
        variables = {"where": {"id": project_id}}
        result = self.auth.client.execute(GQL_PROJECT_DELETE_ASYNCHRONOUSLY, variables)
        return format_result("data", result)

    @typechecked
    def archive_project(self, project_id: str):
        """
        Archive a project.

        Args:
            project_id: Identifier of the project

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.
        """

        variables = {
            "projectID": project_id,
            "archived": True,
        }

        result = self.auth.client.execute(GQL_UPDATE_PROPERTIES_IN_PROJECT, variables)
        return format_result("data", result)

    @typechecked
    def unarchive_project(self, project_id: str):
        """
        Unarchive a project.

        Args:
            project_id: Identifier of the project

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.
        """

        variables = {
            "projectID": project_id,
            "archived": False,
        }

        result = self.auth.client.execute(GQL_UPDATE_PROPERTIES_IN_PROJECT, variables)
        return format_result("data", result)

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
        disable_tqdm: bool = False,
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
        return ProjectCopier(self).copy_project(
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
