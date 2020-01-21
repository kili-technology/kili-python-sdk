import time
from json import dumps, loads
from typing import List

from tqdm import tqdm

from ..helper import GraphQLError, format_result, json_escape
from ..queries.asset import get_assets
from ..queries.label import get_label
from ..queries.project import get_project
from .asset import force_update_status, update_properties_in_asset
from .lock import delete_locks


def create_project(client, title: str, description: str, tool_type: str, use_honeypot: bool,
                   interface_json_settings: str):
    result = client.execute('''
    mutation {
      createProject(
      title: "%s",
      description: "%s",
      toolType: %s,
      useHoneyPot: %s,
      interfaceJsonSettings: "%s") {
        id
      }
    }
    ''' % (title, description, tool_type, str(use_honeypot).lower(), json_escape(interface_json_settings)))
    return format_result('createProject', result)


def delete_project(client, project_id: str):
    result = client.execute('''
    mutation {
      deleteProject(projectID: "%s") {
        id
      }
    }
    ''' % (project_id))
    return format_result('deleteProject', result)


def append_to_roles(client, project_id: str, user_email: str, role: str):
    result = client.execute('''
    mutation {
      appendToRoles(
        projectID: "%s",
        userEmail: "%s",
        role: %s) {
          id
          title
          roles {
              user {
                id
                email
              }
              role
         }
      }
    }
    ''' % (project_id, user_email, role))
    return format_result('appendToRoles', result)


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
    formatted_title = 'null' if title is None else f'"{title}"'
    formatted_description = 'null' if description is None else f'"{description}"'
    formatted_min_consensus_size = 'null' if min_consensus_size is None else int(
        min_consensus_size)
    formatted_min_consensus_size = 'null' if min_consensus_size is None else int(
        min_consensus_size)
    formatted_consensus_tot_coverage = 'null' if consensus_tot_coverage is None else int(
        consensus_tot_coverage)
    formatted_number_of_assets = 'null' if number_of_assets is None else int(
        number_of_assets)
    formatted_number_of_remaining_assets = 'null' if number_of_remaining_assets is None else int(
        number_of_remaining_assets)
    formatted_number_of_assets_with_empty_labels = 'null' if number_of_assets_with_empty_labels is None else int(
        number_of_assets_with_empty_labels)
    formatted_number_of_reviewed_assets = 'null' if number_of_reviewed_assets is None else int(
        number_of_reviewed_assets)
    formatted_number_of_latest_labels = 'null' if number_of_latest_labels is None else int(
        number_of_latest_labels)
    formatted_consensus_mark = 'null' if consensus_mark is None else float(
        consensus_mark)
    formatted_honeypot_mark = 'null' if honeypot_mark is None else float(
        honeypot_mark)
    formatted_instructions = 'null' if instructions is None else f'{dumps(instructions)}'

    result = client.execute('''
        mutation {
          updatePropertiesInProject(
            where: {id: "%s"},
            data: {
              title: %s
              description: %s
              minConsensusSize: %s
              consensusTotCoverage: %s
              numberOfAssets: %s
              numberOfRemainingAssets: %s
              numberOfAssetsWithSkippedLabels: %s
              numberOfReviewedAssets: %s
              numberOfLatestLabels: %s
              consensusMark: %s
              honeypotMark: %s
              instructions: %s
            }
          ) {
            id
          }
        }
        ''' % (project_id, formatted_title, formatted_description,
               formatted_min_consensus_size, formatted_consensus_tot_coverage,
               formatted_number_of_assets, formatted_number_of_remaining_assets,
               formatted_number_of_assets_with_empty_labels, formatted_number_of_reviewed_assets,
               formatted_number_of_latest_labels, formatted_consensus_mark, formatted_honeypot_mark,
               formatted_instructions))
    return format_result('updatePropertiesInProject', result)


def update_interface_in_project(client, project_id: str, jsonSettings: str = None):
    result = client.execute('''
        mutation {
          updatePropertiesInProject(
            where: {id: "%s"},
            data: {
              jsonSettings: """%s""",
            }
          ) {
            id
          }
        }
        ''' % (project_id, jsonSettings))
    return format_result('updatePropertiesInProject', result)


def create_empty_project(client, user_id: str):
    result = client.execute('''
    mutation {
      createEmptyProject(userID: "%s") {
        id

      }
    }
    ''' % (user_id))
    return format_result('createEmptyProject', result)


def update_project(client, project_id: str,
                   title: str,
                   description: str,
                   interface_category: str,
                   creation_active_step: int = 0,
                   creation_completed: List[int] = [0, 1, 2, 3, 4, 5, 6],
                   creation_skipped: List[int] = [],
                   input_type: str = 'TEXT',
                   interface_title: str = None,
                   interface_description: str = None,
                   interface_url: str = None,
                   outsource: bool = False,
                   consensus_tot_coverage: int = 0,
                   min_consensus_size: int = 1,
                   max_worker_count: int = 4,
                   min_agreement: int = 66,
                   use_honey_pot: bool = False,
                   instructions: str = None,
                   model_title: str = "",
                   model_description: str = "",
                   model_url: str = ""):
    formatted_interface_title = 'null' if interface_title is None else f'"{interface_title}"'
    formatted_interface_description = 'null' if interface_description is None else f'"{interface_description}"'
    formatted_interface_url = 'null' if interface_url is None else f'"{interface_url}"'
    formatted_instructions = 'null' if instructions is None else f'"{instructions}"'
    result = client.execute('''
    mutation {
      updateProject(projectID: "%s",
        title: "%s",
        description: "%s",
        creationActiveStep: %d,
        creationCompleted: %s,
        creationSkipped: %s,
        interfaceCategory: %s,
        inputType: %s,
        interfaceTitle: %s,
        interfaceDescription: %s,
        interfaceUrl: %s,
        outsource: %s,
        consensusTotCoverage: %d,
        minConsensusSize: %d,
        maxWorkerCount: %d,
        minAgreement: %d,
        useHoneyPot: %s,
        instructions: %s,
        modelTitle: "%s",
        modelDescription: "%s",
        modelUrl: "%s") {
        id
      }
    }
    ''' % (
        project_id, title, description, creation_active_step, dumps(
            creation_completed),
        dumps(creation_skipped).lower(),
        interface_category, input_type, formatted_interface_title, formatted_interface_description,
        formatted_interface_url, str(
            outsource).lower(),
        consensus_tot_coverage, min_consensus_size, max_worker_count, min_agreement,
        str(use_honey_pot).lower(), formatted_instructions, model_title, model_description, model_url))
    return format_result('updateProject', result)


def update_role(client, role_id: str, project_id: str, user_id: str, role: str):
    result = client.execute('''
    mutation {
      updateRole(roleID: "%s",
        projectID: "%s",
        userID: "%s",
        role: %s) {
          id
      }
    }
    ''' % (role_id, project_id, user_id, role))
    return format_result('updateRole', result)


def delete_from_roles(client, role_id: str):
    result = client.execute('''
    mutation {
      deleteFromRoles(roleID: "%s") {
        id
      }
    }
    ''' % (role_id))
    return format_result('deleteFromRoles', result)


def update_properties_in_project_user(client, project_user_id: str,
                                      total_duration: int = None,
                                      number_of_labeled_assets: int = None,
                                      consensus_mark: float = None,
                                      honeypot_mark: float = None):
    args = [total_duration,
            number_of_labeled_assets, consensus_mark, honeypot_mark]
    formatted_args = ['null' if arg is None else f'{arg}' for arg in args]

    result = client.execute('''
        mutation {
          updatePropertiesInProjectUser(
            where: {id: "%s"},
            data: {
              totalDuration: %s
              numberOfLabeledAssets: %s
              consensusMark: %s
              honeypotMark: %s
            }
          ) {
            id
          }
        }
        ''' % (project_user_id, *formatted_args))
    return format_result('updatePropertiesInProjectUser', result)


def force_project_kpis(client, project_id: str):
    project = get_project(client, project_id=project_id)
    assets = get_assets(client, project_id=project_id)
    numbers_of_labeled_assets = {}
    number_of_latest_labels = 0
    for asset in tqdm(assets):
        asset_updated = force_update_status(client, asset['id'])
        asset['status'] = asset_updated['status']
        unique_asset_authors = list(
            set([label['author']['id'] for label in asset['labels']]))
        json_metadata = asset['jsonMetadata']
        if asset['jsonMetadata'] is not None and not asset['jsonMetadata'].startswith('http') and asset['jsonMetadata'] != '':
            json_metadata = loads(asset['jsonMetadata'])
        update_properties_in_asset(client, asset['id'], external_id=asset['externalId'], priority=asset['priority'],
                                   json_metadata=json_metadata, consensus_mark=asset[
                                       'consensusMark'],
                                   honeypot_mark=asset['honeypotMark'])

        for asset_author in unique_asset_authors:
            numbers_of_labeled_assets[asset_author] = 1 if asset_author not in numbers_of_labeled_assets else \
                numbers_of_labeled_assets[asset_author] + 1

        for label in asset['labels']:
            label_author = label['author']
            if label['isLatestLabelForUser']:
                number_of_latest_labels += 1
            get_label(client, asset_id=asset['id'], user_id=label_author)
        delete_locks(client, asset['id'])
        time.sleep(1)

    # Refresh project
    get_project(client, project_id=project_id)

    number_of_assets = len([a for a in assets if not a['isInstructions']])
    number_of_remaining_assets = len(
        [a for a in assets if a['status'] == 'TODO' or a['status'] == 'ONGOING'])

    update_properties_in_project(client, project_id, number_of_assets=number_of_assets,
                                 number_of_remaining_assets=number_of_remaining_assets,
                                 number_of_latest_labels=number_of_latest_labels,
                                 consensus_mark=project['consensusMark'],
                                 honeypot_mark=project['honeypotMark'])

    project_users = project['roles']
    for project_user in project_users:
        total_duration = project_user['totalDuration']
        user_id = project_user['user']['id']
        number_of_labeled_assets = numbers_of_labeled_assets[
            user_id] if user_id in numbers_of_labeled_assets else 0
        try:
            update_properties_in_project_user(client, project_user['id'], total_duration=total_duration,
                                              number_of_labeled_assets=number_of_labeled_assets,
                                              consensus_mark=project_user['consensusMark'],
                                              honeypot_mark=project_user['honeypotMark'])
        except GraphQLError as e:
            if 'is trying to access projectUser' in str(e):
                print(f'Could not update {user_id}')
            else:
                raise e
