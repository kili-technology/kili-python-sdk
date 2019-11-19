from json import dumps

from ..helper import format_result, json_escape


def create_assets(client, project_id, contents, external_ids):
    result = client.execute('''
    mutation {
      createAssets(
        projectID: "%s",
        contents: %s,
        externalIDs: %s) {
          id
          content
          externalId
          createdAt
          updatedAt
          isHoneypot
          status
          jsonMetadata
      }
    }
    ''' % (project_id, dumps(contents), dumps(external_ids)))
    return format_result('createAssets', result)


def delete_assets_by_external_id(client, project_id, external_id):
    result = client.execute('''
    mutation {
      deleteAssetsByExternalId(projectID: "%s", externalID: "%s") {
        id
      }
    }
    ''' % (project_id, external_id))
    return format_result('deleteAssetsByExternalId', result)


def append_to_dataset(client, project_id, content, external_id, filename='', is_instructions=False,
                      instructions='', is_honeypot=False, status='TODO', json_metadata={}):
    result = client.execute('''
    mutation {
      appendToDataset(projectID: "%s"
        content: "%s",
        externalID: "%s",
        filename: "%s",
        isInstructions: %s,
        instructions: "%s",
        isHoneypot: %s,
        status: %s,
        jsonMetadata: "%s"
      ) {
          id
      }
    }
    ''' % (project_id, content, external_id, filename, str(is_instructions).lower(), instructions,
           str(is_honeypot).lower(), status, json_escape(json_metadata)))
    return format_result('appendToDataset', result)


def append_many_to_dataset(client, project_id, content_array, external_id_array,
                           filename_array=None, is_instructions_array=None, instructions_array=None,
                           is_honeypot_array=None, status_array=None, json_metadata_array=None):
    filename_array = [
        ''] * len(content_array) if not filename_array else filename_array
    is_instructions_array = [
        False] * len(content_array) if not is_instructions_array else is_instructions_array
    instructions_array = [
        ''] * len(content_array) if not instructions_array else instructions_array
    is_honeypot_array = [
        False] * len(content_array) if not is_honeypot_array else is_honeypot_array
    status_array = ['TODO'] * \
        len(content_array) if not status_array else status_array
    json_metadata_array = [
        {}] * len(content_array) if not json_metadata_array else json_metadata_array
    result = client.execute('''
        mutation {
          appendManyToDataset(
            projectID: "%s",
            contentArray: %s,
            externalIDArray: %s,
            filenameArray: %s,
            isInstructionsArray: %s,
            instructionsArray: %s,
            isHoneypotArray: %s,
            statusArray: %s,
            jsonMetadataArray: %s) {
            id
          }
        }
    ''' % (project_id, dumps(content_array), dumps(external_id_array), dumps(filename_array),
           dumps(is_instructions_array).lower(), dumps(
               instructions_array), dumps(is_honeypot_array).lower(),
           dumps(status_array).replace('"', ''), dumps([dumps(elem) for elem in json_metadata_array])))
    return format_result('appendManyToDataset', result)


def update_asset(client, asset_id, project_id, content, external_id, filename, is_instructions, instructions,
                 is_honeypot, consensus_mark, honeypot_mark, status, json_metadata):
    result = client.execute('''
    mutation {
      updateAsset(
        assetID: "%s",
        projectID: "%s",
        content: "%s",
        externalID: "%s",
        filename: "%s",
        isInstructions: %s,
        instructions: "%s",
        isHoneypot: %s,
        consensusMark: %d,
        honeypotMark: %d,
        status: %s,
        jsonMetadata: "%s") {
        id
      }
    }
    ''' % (asset_id, project_id, content, external_id, filename, str(is_instructions).lower(), instructions,
           str(is_honeypot).lower(), consensus_mark, honeypot_mark, status, json_escape(json_metadata)))
    return format_result('updateAsset', result)


def update_properties_in_asset(client, asset_id, external_id=None, priority=None, json_metadata=None, consensus_mark=None, honeypot_mark=None):
    formatted_external_id = 'null' if external_id is None else f'"{external_id}"'
    formatted_priority = 'null' if priority is None else f'{priority}'
    formatted_json_metadata = 'null' if json_metadata is None else f'"{json_escape(json_metadata)}"'
    formatted_consensus_mark = 'null' if consensus_mark is None else f'{consensus_mark}'
    formatted_honeypot_mark = 'null' if honeypot_mark is None else f'{honeypot_mark}'

    result = client.execute('''
        mutation {
          updatePropertiesInAsset(
            where: {id: "%s"},
            data: {
              externalId: %s
              priority: %s
              jsonMetadata: %s
              consensusMark: %s
              honeypotMark: %s
            }
          ) {
            id
          }
        }
        ''' % (asset_id, formatted_external_id, formatted_priority, formatted_json_metadata, formatted_consensus_mark, formatted_honeypot_mark))
    return format_result('updatePropertiesInAsset', result)


def delete_from_dataset(client, asset_id):
    result = client.execute('''
    mutation {
      deleteFromDataset(assetID: "%s") {
        id
      }
    }
    ''' % (asset_id))
    return format_result('deleteFromDataset', result)


def delete_many_from_dataset(client, asset_ids):
    result = client.execute('''
    mutation {
      deleteManyFromDataset(assetIDs: %s) {
        id
      }
    }
    ''' % (dumps(asset_ids)))
    return format_result('deleteManyFromDataset', result)


def force_update_status(client, asset_id):
    result = client.execute('''
    mutation {
      forceUpdateStatus(assetID: "%s") {
        id
        status
      }
    }
    ''' % (asset_id))
    return format_result('forceUpdateStatus', result)
