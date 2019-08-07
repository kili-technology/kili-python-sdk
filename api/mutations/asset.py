from json import dumps, loads


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
    return loads(result)['data']['createAssets']


def delete_assets_by_external_id(client, project_id, external_id):
    result = client.execute('''
    mutation {
      deleteAssetsByExternalId(projectID: "%s", externalID: "%s") {
        id
      }
    }
    ''' % (project_id, external_id))
    return loads(result)['data']['deleteAssetsByExternalId']


def kili_append_to_dataset(client, project_id, content, external_id, filename, is_instructions,
                           instructions, is_honeypot, consensus_mark, honeypot_mark, status):
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
        status: %s) {
        id
      }
    }
    ''' % (project_id, content, external_id, filename, str(is_instructions).lower(),
           instructions, str(is_honeypot).lower(), consensus_mark, honeypot_mark, status))
    return loads(result)['data']['appendToDataset']
