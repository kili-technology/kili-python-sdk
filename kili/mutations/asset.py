from json import dumps

from ..helper import format_result


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


def kili_append_to_dataset(client, project_id, content, external_id, filename, is_instructions,
                           instructions, is_honeypot, consensus_mark, honeypot_mark, status, json_metadata):
    result = client.execute('''
    mutation {
      appendToDataset(projectID: "%s"
        content: "%s",
        externalID: "%s",
        filename: "%s",
        isInstructions: %s,
        instructions: "%s",
        isHoneypot: %s,
        consensusMark: %d,
        honeypotMark: %d,
        status: %s, 
        jsonMetadata: "%s"
      ) {
          id
      }
    }
    ''' % (project_id, content, external_id, filename, str(is_instructions).lower(), instructions,
           str(is_honeypot).lower(), consensus_mark, honeypot_mark, status, json_metadata))
    return format_result('appendToDataset', result)
