from json import loads

def get_projects(client, user_id):
    result = client.execute('''
    query {
      getProjects(userID: "%s") {
        id
        title
        description
        author {
            id
            email
        }
        createdAt
        interfaceTools {
            name
            toolType
            jsonSettings
        }
        roles {
            user {
                id
                email
            }
            role
            lastLabelingAt
            numberOfAnnotations
            totalDuration
            durationPerLabel
            honeypotMark
        }
        updatedAt
        useHoneyPot
        numberOfAssets
        completionPercentage
        numberOfAssetsWithoutLabel
        numberOfAssetsWithEmptyLabels
        numberOfReviewedAssets
        numberOfLatestLabels
        dataset {
          id
          honeypotMark
        }
      }
    }
    ''' % (user_id))
    return loads(result)['data']['getProjects']


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
    return loads(result)['data']['getAssetsByExternalId']


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
        status
        labels {
          author {
            id
            email
          }
          labelType
          jsonResponse
          createdAt
          millisecondsToLabel
          totalMillisecondsToLabel
          honeypotMark
        }
      }
    }
    ''' % (project_id))
    return loads(result)['data']['exportAssets']
