def get_asset(client, asset_id):
    result = client.execute('''
    query {
      getAsset(assetID: "%s") {
        id
      }
    }
    ''' % (asset_id))
    return loads(result)['data']['getAsset']


def get_assets(client, project_id, skip, first):
    result = client.execute('''
    query {
      getAssets(projectID: "%s", skip: %d, first: %d) {
        id
        externalId
        content
        filename
        isInstructions
        instructions
        isHoneypot
        consensusMark
        honeypotMark
        status
        isUsedForConsensus
        labels {
          id
          labelType
          jsonResponse
          author {
          id
          }
      }
      }
    }
    ''' % (project_id, skip, first))
    return loads(result)['data']['getAssets']


def get_assets_by_external_id(client, project_id, asset_id):
    result = client.execute('''
    query {
      getAssetsByExternalId(projectID: "%s", externalID: "%s") {
        id
        externalId
        content
        filename
        isInstructions
        instructions
        isHoneypot
        consensusMark
        honeypotMark
        status
        isUsedForConsensus
      }
    }
    ''' % (project_id, asset_id))
    data = loads(result)['data']['getAssetsByExternalId']
    return data if data else []


def get_next_asset_from_label(client, label_asset_id, want_instructions_only):
    result = client.execute('''
    query {
      getNextAssetFromLabel(labelAssetID: "%s", wantInstructionsOnly: %s) {
        id
      }
    }
    ''' % (label_asset_id, str(want_instructions_only).lower()))
    return loads(result)['data']['getNextAssetFromLabel']


def get_next_asset_from_project(client, project_id, want_instructions_only):
    result = client.execute('''
    query {
      getNextAssetFromProject(projectID: "%s", wantInstructionsOnly: %s) {
        id
      }
    }
    ''' % (project_id, str(want_instructions_only).lower()))
    return loads(result)['data']['getNextAssetFromProject']
