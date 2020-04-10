import time
from json import dumps, loads
from typing import List

from tqdm import tqdm

from ...helpers import GraphQLError, format_result
from ...queries.asset import get_assets
from ...queries.label import get_label
from ...queries.project import get_project
from ..asset import update_properties_in_asset
from .queries import (GQL_APPEND_TO_ROLES, GQL_CREATE_EMPTY_PROJECT,
                      GQL_DELETE_FROM_ROLES,
                      GQL_GQL_UPDATE_PROPERTIES_IN_PROJECT_USER,
                      GQL_UPDATE_PROJECT, GQL_UPDATE_PROPERTIES_IN_PROJECT,
                      GQL_UPDATE_ROLE)


def append_to_roles(client, project_id: str, user_email: str, role: str):
    variables = {
        'projectID': project_id,
        'userEmail': user_email,
        'role': role
    }
    result = client.execute(GQL_APPEND_TO_ROLES, variables)
    return format_result('data', result)


def update_properties_in_project(client, project_id: str,
                                 consensus_mark: float = None,
                                 consensus_tot_coverage: int = None,
                                 description: str = None,
                                 honeypot_mark: float = None,
                                 instructions: str = None,
                                 interface_category: str = 'IV2',
                                 json_interface: dict = None,
                                 min_consensus_size: int = None,
                                 number_of_assets: int = None,
                                 number_of_assets_with_empty_labels: int = None,
                                 number_of_latest_labels: int = None,
                                 number_of_remaining_assets: int = None,
                                 number_of_reviewed_assets: int = None,
                                 title: str = None):
    variables = {
        'consensusMark': consensus_mark,
        'consensusTotCoverage': consensus_tot_coverage,
        'description': description,
        'honeypotMark': honeypot_mark,
        'instructions': instructions,
        'interfaceCategory': interface_category,
        'jsonInterface': dumps(json_interface) if json_interface is not None else None,
        'minConsensusSize': min_consensus_size,
        'numberOfAssets': number_of_assets,
        'numberOfAssetsWithSkippedLabels': number_of_assets_with_empty_labels,
        'numberOfLatestLabels': number_of_latest_labels,
        'numberOfRemainingAssets': number_of_remaining_assets,
        'numberOfReviewedAssets': number_of_reviewed_assets,
        'projectID': project_id,
        'title': title
    }
    result = client.execute(GQL_UPDATE_PROPERTIES_IN_PROJECT, variables)
    return format_result('data', result)


def create_empty_project(client, user_id: str):
    variables = {'userID': user_id}
    result = client.execute(GQL_CREATE_EMPTY_PROJECT, variables)
    return format_result('data', result)


def update_project(client, project_id: str,
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
    result = client.execute(GQL_UPDATE_PROJECT, variables)
    return format_result('data', result)


def update_role(client, role_id: str, project_id: str, user_id: str, role: str):
    variables = {
        'roleID': role_id,
        'projectID': project_id,
        'userID': user_id,
        'role': role
    }
    result = client.execute(GQL_UPDATE_ROLE, variables)
    return format_result('data', result)


def delete_from_roles(client, role_id: str):
    variables = {'roleID': role_id}
    result = client.execute(GQL_DELETE_FROM_ROLES, variables)
    return format_result('data', result)


def update_properties_in_project_user(client, project_user_id: str,
                                      consensus_mark: float = None,
                                      honeypot_mark: float = None,
                                      json_interface: dict = None,
                                      number_of_labeled_assets: int = None,
                                      total_duration: int = None):
    variables = {
        'consensusMark': consensus_mark,
        'honeypotMark': honeypot_mark,
        'jsonInterface': dumps(json_interface),
        'numberOfLabeledAssets': number_of_labeled_assets,
        'projectUserID': project_user_id,
        'totalDuration': total_duration,
    }
    result = client.execute(
        GQL_GQL_UPDATE_PROPERTIES_IN_PROJECT_USER, variables)
    return format_result('data', result)


def force_project_kpis(client, project_id: str):
    _ = get_assets(client, project_id=project_id)
    _ = get_project(client, project_id=project_id)
