from ..helper import format_result


def get_asset(client, asset_id):
    result = client.execute('''
    query {
      getAsset(assetID: "%s") {
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
          createdAt
          secondsToLabel
          totalSecondsToLabel
          labelType
          jsonResponse
          isLatestLabelForUser
          author {
            id
          }
        }
        locks {
          id
          author {
            email
          }
          createdAt
          lockType
        }
      }
    }
    ''' % (asset_id))
    return format_result('getAsset', result)


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
        calculatedConsensusMark
        calculatedHoneypotMark
        consensusMark
        honeypotMark
        status
        isUsedForConsensus
        jsonMetadata
        priority
        labels {
          id
          createdAt
          labelType
          jsonResponse
          isLatestLabelForUser
          author {
            id
          }
        }
      }
    }
    ''' % (project_id, skip, first))
    return format_result('getAssets', result)


def get_assets_by_external_id(client, project_id, external_id):
    result = client.execute('''
    query {
      getAssetsByExternalId(projectID: "%s", externalID: "%s") {
          id
          content
          externalId
          createdAt
          updatedAt
          isHoneypot
          isUsedForConsensus
          status
          labels {
            author {
              id
              email
            }
            labelType
            jsonResponse
            createdAt
            secondsToLabel
            totalSecondsToLabel
            honeypotMark
          }
      }
    }
    ''' % (project_id, external_id))
    return format_result('getAssetsByExternalId', result)


def get_next_asset_from_label(client, label_asset_id, want_instructions_only, in_review):
    result = client.execute('''
    query {
      getNextAssetFromLabel(labelAssetID: "%s", wantInstructionsOnly: %s, inReview: %s, where: {}) {
        id
      }
    }
    ''' % (label_asset_id, str(want_instructions_only).lower(), str(in_review).lower()))
    return format_result('getNextAssetFromLabel', result)


def get_next_asset_from_project(client, project_id, want_instructions_only, in_review):
    result = client.execute('''
    query {
      getNextAssetFromProject(projectID: "%s", wantInstructionsOnly: %s, inReview: %s) {
        id
      }
    }
    ''' % (project_id, str(want_instructions_only).lower(), str(in_review).lower()))
    return format_result('getNextAssetFromProject', result)


def export_assets(client, project_id):
    result = client.execute('''
    query {
      exportAssets(projectID: "%s") {
        id
        content
        externalId
        createdAt
        updatedAt
        isHoneypot
        isInstructions
        status
        labels {
          id
          author {
            id
            email
          }
          labelType
          jsonResponse
          createdAt
          secondsToLabel
          totalSecondsToLabel
          honeypotMark
        }
      }
    }
    ''' % (project_id))
    return format_result('exportAssets', result)
