import time
from json import dumps, loads
from typing import List

from tqdm import tqdm

from ...helpers import GraphQLError, format_result
from ...queries.asset import QueriesAsset
from ...queries.project import QueriesProject
from .queries import (GQL_APPEND_TO_ROLES, GQL_CREATE_EMPTY_PROJECT,
                      GQL_DELETE_FROM_ROLES,
                      GQL_GQL_UPDATE_PROPERTIES_IN_PROJECT_USER,
                      GQL_UPDATE_PROJECT, GQL_UPDATE_PROPERTIES_IN_PROJECT,
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
            'title': title
        }
        result = self.auth.client.execute(
            GQL_UPDATE_PROPERTIES_IN_PROJECT, variables)
        return format_result('data', result)

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

    def update_project(self, project_id: str,
                       title: str,
                       description: str,
                       interface_category: str,
                       input_type: str = 'TEXT',
                       consensus_tot_coverage: int = 0,
                       min_consensus_size: int = 1,
                       max_worker_count: int = 4,
                       min_agreement: int = 66,
                       use_honey_pot: bool = False,
                       instructions: str = None):
        """
        Update a project

        Parameters
        ----------
        - project_id : str
        - title : str
        - description : str
        - interface_category : str
            Currently, one of
            {IV2, ALL, CLASSIFICATION, SENTIMENT, NER, NER_WITH_RELATIONS,
            RELATION_EXTRACTION, ENTITY_GROUPING, COREFERENCE_RESOLUTION,
            TRANSLATION, TRANSCRIPTION, IMAGE, MULTICLASS_IMAGE, CUSTOM,
            IMAGE_TO_GRAPH, IMAGE_WITH_SEARCH, IMAGE_TO_TEXT, MULTICLASS_TEXT_CLASSIFICATION,
            SINGLECLASS_TEXT_CLASSIFICATION, MULTICLASS_IMAGE_CLASSIFICATION,
            SINGLECLASS_IMAGE_CLASSIFICATION, VIDEO_CLASSIFICATION, NA}
        - input_type : str, optional (default = 'TEXT')
            Currently, one of {AUDIO, IMAGE, PDF, TEXT, URL, VIDEO, NA}
        - consensus_tot_coverage : int, optional (default = 0)
            Should be between 0 and 100. It is the percentage of the dataset
            that will be annotated several times.
        - min_consensus_size : int, optional (default = 1)
            Number of people that will annotate the same asset, for consensus computation.
        - max_worker_count : int, optional (default = 4)
            Maximum number of workers in the project
        - min_agreement : int, optional (default = 66)
            Should be a percentage (between 0 and 100)
        - use_honey_pot : bool, optional (default = False)
            Whether to compute honeypot in the project
        - instructions : str, optional (default = None)
            You can give instructions, they will be available to the annotators during the labeling process.
        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.
        """
        variables = {
            'projectID': project_id,
            'title': title,
            'description': description,
            'interfaceCategory': interface_category,
            'inputType': input_type,
            'consensusTotCoverage': consensus_tot_coverage,
            'minConsensusSize': min_consensus_size,
            'maxWorkerCount': max_worker_count,
            'minAgreement': min_agreement,
            'useHoneyPot': use_honey_pot,
            'instructions': instructions
        }
        result = self.auth.client.execute(GQL_UPDATE_PROJECT, variables)
        return format_result('data', result)

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

    def update_properties_in_project_user(self, project_user_id: str,
                                          consensus_mark: float = None,
                                          honeypot_mark: float = None,
                                          json_interface: dict = None,
                                          number_of_labeled_assets: int = None,
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
        - total_duration : int, optional (default = None)
            Total time the user spent in the project.

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.
        """
        variables = {
            'consensusMark': consensus_mark,
            'honeypotMark': honeypot_mark,
            'jsonInterface': dumps(json_interface),
            'numberOfLabeledAssets': number_of_labeled_assets,
            'projectUserID': project_user_id,
            'totalDuration': total_duration,
        }
        result = self.auth.client.execute(
            GQL_GQL_UPDATE_PROPERTIES_IN_PROJECT_USER, variables)
        return format_result('data', result)

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
