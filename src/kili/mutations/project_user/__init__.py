"""Project User mutations."""
from typing import Optional

from typeguard import typechecked

from ...helpers import format_result


# pylint: disable=too-few-public-methods, too-many-arguments
class MutationsProjectUser:
    """
    Holds the mutations of the ProjectUser
    """

    def __init__(self, auth):
        """Initialize the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    @typechecked
    def update_properties_in_project_user(
        self,
        project_user_id: str,
        consensus_mark: Optional[float] = None,
        honeypot_mark: Optional[float] = None,
        number_of_labeled_assets: Optional[int] = None,
        starred: Optional[bool] = None,
        total_duration: Optional[int] = None,
    ):
        """
        Update properties of a project-user tuple

        Args:
            project_user_id: Identifier of the project user
            consensus_mark: Should be between 0 and 1.
            honeypot_mark: Should be between 0 and 1.
            number_of_labeled_assets: Number of assets the user labeled in the project.
            starred: Whether to star the project in the project list.
            total_duration: Total time the user spent in the project.

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.

        Examples:
            >>> for project_user in project_users:
            ...     kili.update_properties_in_project_user(
                        project_user_id=project_user['id'],
                        honeypot_mark=0)
        """
        variables = {
            "consensusMark": consensus_mark,
            "honeypotMark": honeypot_mark,
            "numberOfLabeledAssets": number_of_labeled_assets,
            "projectUserID": project_user_id,
            "starred": starred,
            "totalDuration": total_duration,
        }
        result = self.auth.client.execute(
            """
                mutation(
                    $projectUserID: ID!
                    $totalDuration: Int
                    $numberOfLabeledAssets: Int
                    $starred: Boolean
                    $consensusMark: Float
                    $honeypotMark: Float
                ) {{
                data: updatePropertiesInProjectUser(
                    where: {{id: $projectUserID}},
                    data: {{
                        totalDuration: $totalDuration
                        numberOfLabeledAssets: $numberOfLabeledAssets
                        starred: $starred
                        consensusMark: $consensusMark
                        honeypotMark: $honeypotMark
                    }}
                ) {{
                    id
                }}
                }}
            """,
            variables,
        )
        return format_result("data", result)
