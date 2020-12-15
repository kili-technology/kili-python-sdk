import time
from json import dumps, loads
from typing import List

from tqdm import tqdm

from ...helpers import Compatible, GraphQLError, format_result
from ...queries.asset import QueriesAsset
from ...queries.project import QueriesProject
from .queries import (GQL_APPEND_TO_ROLES, GQL_CREATE_EMPTY_PROJECT, GQL_CREATE_PROJECT,
                      GQL_DELETE_FROM_ROLES,
                      GQL_DELETE_PROJECT,
                      GQL_GQL_UPDATE_PROPERTIES_IN_PROJECT_USER,
                      GQL_UPDATE_PROPERTIES_IN_PROJECT,
                      GQL_UPDATE_PROPERTIES_IN_ROLE)


class MutationsProject:

    def __init__(self, auth):
        """
        Initializes the subclass

        Parameters
        ----------
        - auth : KiliAuth object
        """
        self.auth = auth

    @Compatible(['v1', 'v2'])
    def append_to_roles(self, project_id: str, user_email: str, role: str):
        """
        Add a user to a project

        If the user does not exist in your organization, he is invited and added 
        both to your organization and project. This function can also be used to change 
        the role of the user in the project.

        Parameters
        ----------
        - project_id : str
            Id of the project.
        - user_email : str
            The email of the user. This email is used as the unique identifier of the user.
        - role : str
            One of {"ADMIN", "REVIEWER", "LABELER", "READER"}.

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.
        """
        variables = {
            'projectID': project_id,
            'userEmail': user_email,
            'role': role
        }
        result = self.auth.client.execute(GQL_APPEND_TO_ROLES, variables)
        return format_result('data', result)

    @Compatible(['v1', 'v2'])
    def update_properties_in_project(self, project_id: str,
                                     consensus_mark: float = None,
                                     consensus_tot_coverage: int = None,
                                     description: str = None,
                                     honeypot_mark: float = None,
                                     instructions: str = None,
                                     interface_category: str = 'IV2',
                                     input_type: str = None,
                                     json_interface: dict = None,
                                     min_consensus_size: int = None,
                                     number_of_assets: int = None,
                                     number_of_assets_with_empty_labels: int = None,
                                     number_of_remaining_assets: int = None,
                                     number_of_reviewed_assets: int = None,
                                     should_relaunch_kpi_computation: bool = None,
                                     title: str = None):
        """
        Update properties of a project

        Parameters
        ----------
        - project_id : str
            Identifier of the project
        - consensus_mark : float, optional (default = None)
            Should be between 0 and 1
        - consensus_tot_coverage : int, optional (default = None)
            Should be between 0 and 100. It is the percentage of the dataset
            that will be annotated several times.
        - description : str, optional (default = None)
        - honeypot_mark : float, optional (default = None)
            Should be between 0 and 1
        - instructions : str, optional (default = None)
        - interface_category : str, optional (default = 'IV2')
            Always use 'IV2'
        - input_type : str, optional (default = None)
            Currently, one of {AUDIO, IMAGE, PDF, TEXT, URL, VIDEO, NA}
        - json_interface : dict, optional (default = None)
            The json parameters of the project, see Edit your interface.
        - min_consensus_size : int, optional (default = None)
            Number of people that will annotate the same asset, for consensus computation.
        - number_of_assets : int, optional (default = None)
            Defaults to 0
        - number_of_assets_with_empty_labels : int, optional (default = None)
            Defaults to 0
        - number_of_remaining_assets : int, optional (default = None)
            Defaults to 0
        - number_of_reviewed_assets : int, optional (default = None)
            Defaults to 0
        - should_relaunch_kpi_computation : bool, optional (default = None)
            Technical field, added to indicate changes in honeypot or consensus settings
        - title : str, optional (default = None)

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.
        """
        variables = {
            'consensusMark': consensus_mark,
            'consensusTotCoverage': consensus_tot_coverage,
            'description': description,
            'honeypotMark': honeypot_mark,
            'instructions': instructions,
            'interfaceCategory': interface_category,
            'inputType': input_type,
            'jsonInterface': dumps(json_interface) if json_interface is not None else None,
            'minConsensusSize': min_consensus_size,
            'numberOfAssets': number_of_assets,
            'numberOfAssetsWithSkippedLabels': number_of_assets_with_empty_labels,
            'numberOfRemainingAssets': number_of_remaining_assets,
            'numberOfReviewedAssets': number_of_reviewed_assets,
            'projectID': project_id,
            'shouldRelaunchKpiComputation': should_relaunch_kpi_computation,
            'title': title
        }
        result = self.auth.client.execute(
            GQL_UPDATE_PROPERTIES_IN_PROJECT, variables)
        return format_result('data', result)

    @Compatible(endpoints=['v1', 'v2'])
    def create_empty_project(self, user_id: str):
        """
        Create an empty project

        Parameters
        ----------
        - user_id : str

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.
        """
        variables = {'userID': user_id}
        result = self.auth.client.execute(GQL_CREATE_EMPTY_PROJECT, variables)
        return format_result('data', result)

    @Compatible(endpoints=['v2'])
    def create_project(self, description: str, input_type: str, json_interface: dict, title: str, user_id: str, project_type: str = None):
        """
        Create an project

        Parameters
        ----------
        - description : str
        - input_type : str
            Currently, one of {AUDIO, IMAGE, PDF, TEXT, URL, VIDEO, NA}
        - json_interface: dict
            The json parameters of the project, see Edit your interface.
        - project_type: str, optional (default = None)
            Currently, one of {IMAGE_CLASSIFICATION_SINGLE, IMAGE_CLASSIFICATION_MULTI, IMAGE_OBJECT_DETECTION_RECTANGLE, IMAGE_OBJECT_DETECTION_POLYGON, IMAGE_OBJECT_DETECTION_SEMANTIC, OCR, PDF_CLASSIFICATION_SINGLE, PDF_CLASSIFICATION_MULTI, TEXT_CLASSIFICATION_SINGLE, TEXT_CLASSIFICATION_MULTI, TEXT_TRANSCRIPTION, TEXT_NER, VIDEO_CLASSIFICATION_SINGLE, VIDEO_FRAME_CLASSIFICATION, VIDEO_FRAME_OBJECT_TRACKING, SPEECH_TO_TEXT}
        - title : str
        - user_id : str

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.
        """
        variables = {
            'description': description,
            'inputType': input_type,
            'jsonInterface': dumps(json_interface),
            'projectType': project_type,
            'title': title,
            'userID': user_id
        }
        result = self.auth.client.execute(GQL_CREATE_PROJECT, variables)
        return format_result('data', result)

    @Compatible(['v1', 'v2'])
    def update_properties_in_role(self, role_id: str, project_id: str, user_id: str, role: str):
        """
        Update properties of a role

        You should be either an admin or a reviewer of the project, or an admin of the
        organization to be able to change the role of somebody.

        Parameters
        ----------
        - role_id : str
            Role identifier of the user. E.g. : 'to-be-deactivated'
        - project_id : str
            Identifier of the project
        - user_id : str
            The email or identifier of the user with updated role
        - role : str
            The new role. One of "ADMIN", "REVIEWER", "LABELER", "READER"

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.
        """
        variables = {
            'roleID': role_id,
            'projectID': project_id,
            'userID': user_id,
            'role': role
        }
        result = self.auth.client.execute(
            GQL_UPDATE_PROPERTIES_IN_ROLE, variables)
        return format_result('data', result)

    @Compatible(['v1', 'v2'])
    def delete_from_roles(self, role_id: str):
        """
        Delete users by their role_id

        Parameters
        ----------
        - role_id : str

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.
        """
        variables = {'roleID': role_id}
        result = self.auth.client.execute(GQL_DELETE_FROM_ROLES, variables)
        return format_result('data', result)

    @Compatible(['v2'])
    def update_properties_in_project_user(self, project_user_id: str,
                                          consensus_mark: float = None,
                                          honeypot_mark: float = None,
                                          number_of_labeled_assets: int = None,
                                          starred: bool = None,
                                          total_duration: int = None):
        """
        Update properties of a project-user tuple

        Parameters
        ----------
        - project_user_id : str
        - consensus_mark : float, optional (default = None)
            Should be between 0 and 1.
        - honeypot_mark : float, optional (default = None)
            Should be between 0 and 1.
        - json_interface : dict, optional (default = None)
            The json parameters of the project, see Edit your interface.
        - number_of_labeled_assets : int, optional (default = None)
            Number of assets the user labeled in the project.
        - starred : bool, optional (default = None)
            Whether to star the project in the project list.
        - total_duration : int, optional (default = None)
            Total time the user spent in the project.

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.
        """
        variables = {
            'consensusMark': consensus_mark,
            'honeypotMark': honeypot_mark,
            'numberOfLabeledAssets': number_of_labeled_assets,
            'projectUserID': project_user_id,
            'starred': starred,
            'totalDuration': total_duration,
        }
        result = self.auth.client.execute(
            GQL_GQL_UPDATE_PROPERTIES_IN_PROJECT_USER, variables)
        return format_result('data', result)

    @Compatible()
    def force_project_kpis(self, project_id: str):
        """
        Compute KPIs for a project

        Parameters
        ----------
        - project_id : str

        Returns
        -------
        - None
        """
        _ = QueriesAsset(self.auth).assets(project_id=project_id)
        _ = QueriesProject(self.auth).projects(project_id=project_id)

    @Compatible(['v1', 'v2'])
    def delete_project(self, project_id: str):
        """
        Delete project permanently 

        Parameters
        ----------
        - project_id : str

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.
        """
        variables = {'projectID': project_id}
        result = self.auth.client.execute(GQL_DELETE_PROJECT, variables)
        return format_result('data', result)
