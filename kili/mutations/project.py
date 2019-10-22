from json import dumps
from tqdm import tqdm

from ..helper import format_result, json_escape
from ..queries.asset import export_assets, get_assets
from .asset import force_update_status


def create_project(client, title, description, tool_type, use_honeypot, interface_json_settings):
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


def delete_project(client, project_id):
    result = client.execute('''
    mutation {
      deleteProject(projectID: "%s") {
        id
      }
    }
    ''' % (project_id))
    return format_result('deleteProject', result)


def append_to_roles(client, project_id, user_email, role):
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


def update_properties_in_project(client, project_id, min_consensus_size=None, consensus_tot_coverage=None,
                                 number_of_assets=None,
                                 completion_percentage=None,
                                 number_of_remaining_assets=None,
                                 number_of_assets_with_empty_labels=None,
                                 number_of_reviewed_assets=None,
                                 number_of_latest_labels=None):
    formatted_min_consensus_size = 'null' if min_consensus_size is None else int(
        min_consensus_size)
    formatted_consensus_tot_coverage = 'null' if consensus_tot_coverage is None else int(
        consensus_tot_coverage)
    formatted_number_of_assets = 'null' if number_of_assets is None else int(
        number_of_assets)
    formatted_completion_percentage = 'null' if completion_percentage is None else completion_percentage
    formatted_number_of_remaining_assets = 'null' if number_of_remaining_assets is None else int(
        number_of_remaining_assets)
    formatted_number_of_assets_with_empty_labels = 'null' if number_of_assets_with_empty_labels is None else int(
        number_of_assets_with_empty_labels)
    formatted_number_of_reviewed_assets = 'null' if number_of_reviewed_assets is None else int(
        number_of_reviewed_assets)
    formatted_number_of_latest_labels = 'null' if number_of_latest_labels is None else int(
        number_of_latest_labels)

    result = client.execute('''
        mutation {
          updatePropertiesInProject(
            where: {id: "%s"},
            data: {
              minConsensusSize: %s
              consensusTotCoverage: %s
              numberOfAssets: %s
              completionPercentage: %s
              numberOfRemainingAssets: %s
              numberOfAssetsWithSkippedLabels: %s
              numberOfReviewedAssets: %s
              numberOfLatestLabels: %s
            }
          ) {
            id
          }
        }
        ''' % (project_id, formatted_min_consensus_size, formatted_consensus_tot_coverage,
               formatted_number_of_assets, formatted_completion_percentage, formatted_number_of_remaining_assets,
               formatted_number_of_assets_with_empty_labels, formatted_number_of_reviewed_assets, formatted_number_of_latest_labels))
    return format_result('updatePropertiesInProject', result)


def update_interface_in_project(client, project_id, jsonSettings=None):
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


def force_project_kpi_computation(client, project_id):
    result = client.execute('''
    mutation {
      forceProjectKpiComputation(projectID: "%s") {
        id
        numberOfAssets
        completionPercentage
        numberOfRemainingAssets
        numberOfAssetsWithSkippedLabels
        numberOfReviewedAssets
        numberOfLatestLabels
        roles {
          user { id }
          lastLabelingAt
          numberOfAnnotations
          numberOfLabeledAssets
          totalDuration
          durationPerLabel
          honeypotMark
        }
        dataset {
          id
          honeypotMark
        }
      }
    }
    ''' % (project_id))
    return format_result('forceProjectKpiComputation', result)


def frontend_create_project(client, user_id):
    result = client.execute('''
    mutation {
      frontendCreateProject(userID: "%s") {
        id

      }
    }
    ''' % (user_id))
    return format_result('frontendCreateProject', result)


def update_project(client, project_id,
                   title,
                   description,
                   creation_active_step,
                   creation_completed,
                   creation_skipped,
                   interface_category,
                   input_type,
                   interface_title,
                   interface_description,
                   interface_url,
                   outsource,
                   consensus_tot_coverage,
                   min_consensus_size,
                   max_worker_count,
                   min_agreement,
                   use_honey_pot,
                   instructions,
                   model_title,
                   model_description,
                   model_url):
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
        interfaceTitle: "%s",
        interfaceDescription: "%s",
        interfaceUrl: "%s",
        outsource: %s,
        consensusTotCoverage: %d,
        minConsensusSize: %d,
        maxWorkerCount: %d,
        minAgreement: %d,
        useHoneyPot: %s,
        instructions: "%s",
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
        interface_category, input_type, interface_title, interface_description, interface_url, str(
            outsource).lower(),
        consensus_tot_coverage, min_consensus_size, max_worker_count, min_agreement,
        str(use_honey_pot).lower(), instructions, model_title, model_description, model_url))
    return format_result('updateProject', result)


def update_role(client, role_id, project_id, user_id, role):
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


def delete_from_roles(client, role_id):
    result = client.execute('''
    mutation {
      deleteFromRoles(roleID: "%s") {
        id
      }
    }
    ''' % (role_id))
    return format_result('deleteFromRoles', result)


def update_properties_in_project_user(client, project_user_id, total_duration=None, duration_per_label=None):
    formatted_total_duration = 'null' if total_duration is None else f'{total_duration}'
    formatted_duration_per_label = 'null' if duration_per_label is None else f'{duration_per_label}'

    result = client.execute('''
        mutation {
          updatePropertiesInProjectUser(
            where: {id: "%s"},
            data: {
              totalDuration: %s
              durationPerLabel: %s
            }
          ) {
            id
          }
        }
        ''' % (project_user_id, formatted_total_duration, formatted_duration_per_label))
    return format_result('updatePropertiesInProjectUser', result)


def force_project_kpis(client, project_id):
    assets = get_assets(client, project_id, 0, 100000000)
    for asset in tqdm(assets):
        asset_updated = force_update_status(client, asset['id'])
        asset['status'] = asset_updated['status']
    number_of_assets = len([a for a in assets if not a['isInstructions']])
    number_of_remaining_assets = len(
        [a for a in assets if a['status'] == 'TODO' or a['status'] == 'ONGOING'])
    completion_percentage = 1 - number_of_remaining_assets / number_of_assets
    update_properties_in_project(client, project_id, number_of_assets=number_of_assets,
                                 number_of_remaining_assets=number_of_remaining_assets, completion_percentage=completion_percentage)
