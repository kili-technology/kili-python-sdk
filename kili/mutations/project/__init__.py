import time
from json import dumps, loads
from typing import List

from tqdm import tqdm

from ...helpers import GraphQLError, format_result
from ...queries.asset import get_assets
from ...queries.label import get_label
from ...queries.project import get_project
from ..asset import update_properties_in_asset
from ..lock import delete_locks
from .queries import (GQL_APPEND_TO_ROLES, GQL_CREATE_EMPTY_PROJECT,
                      GQL_CREATE_PROJECT, GQL_DELETE_FROM_ROLES,
                      GQL_GQL_UPDATE_PROPERTIES_IN_PROJECT_USER,
                      GQL_UPDATE_PROJECT, GQL_UPDATE_PROPERTIES_IN_PROJECT,
                      GQL_UPDATE_ROLE)


def create_project(client, title: str, description: str, use_honeypot: bool,
                   interface_json_settings: dict):
    variables = {
        'title': title,
        'description': description,
        'useHoneyPot': use_honeypot,
        'interfaceJsonSettings': dumps(interface_json_settings)
    }
    result = client.execute(GQL_CREATE_PROJECT, variables)
    return format_result('data', result)


def append_to_roles(client, project_id: str, user_email: str, role: str):
    variables = {
        'projectID': project_id,
        'userEmail': user_email,
        'role': role
    }
    result = client.execute(GQL_APPEND_TO_ROLES, variables)
    return format_result('data', result)


def update_properties_in_project(client, project_id: str,
                                 title: str = None,
                                 description: str = None,
                                 min_consensus_size: int = None,
                                 consensus_tot_coverage: int = None,
                                 number_of_assets: int = None,
                                 number_of_remaining_assets: int = None,
                                 number_of_assets_with_empty_labels: int = None,
                                 number_of_reviewed_assets: int = None,
                                 number_of_latest_labels: int = None,
                                 consensus_mark: float = None,
                                 honeypot_mark: float = None,
                                 instructions: str = None):
    variables = {
        'projectID': project_id,
        'title': title,
        'description': description,
        'minConsensusSize': min_consensus_size,
        'consensusTotCoverage': consensus_tot_coverage,
        'numberOfAssets': number_of_assets,
        'numberOfRemainingAssets': number_of_remaining_assets,
        'numberOfAssetsWithSkippedLabels': number_of_assets_with_empty_labels,
        'numberOfReviewedAssets': number_of_reviewed_assets,
        'numberOfLatestLabels': number_of_latest_labels,
        'consensusMark': consensus_mark,
        'honeypotMark': honeypot_mark,
        'instructions': instructions
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
                                      total_duration: int = None,
                                      number_of_labeled_assets: int = None,
                                      consensus_mark: float = None,
                                      honeypot_mark: float = None):
    variables = {
        'projectUserID': project_user_id,
        'totalDuration': total_duration,
        'numberOfLabeledAssets': number_of_labeled_assets,
        'consensusMark': consensus_mark,
        'honeypotMark': honeypot_mark
    }
    result = client.execute(
        GQL_GQL_UPDATE_PROPERTIES_IN_PROJECT_USER, variables)
    return format_result('data', result)


def force_project_kpis(client, project_id: str):
    _ = get_assets(client, project_id=project_id)
    _ = get_project(client, project_id=project_id)
