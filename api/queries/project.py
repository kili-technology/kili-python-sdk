from json import loads


def get_projects(client, user_id):
    result = client.execute('''
    query {
      getProjects(userID: "%s") {
        id
        title
        numberOfAssets
        completionPercentage
        numberOfAssetsWithoutLabel
        numberOfAssetsWithEmptyLabels
        numberOfReviewedAssets
        numberOfLatestLabels
        roles {
          user { id }
          lastLabelingAt
          numberOfAnnotations
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
    ''' % (user_id))
    return loads(result)['data']['getProjects']


def get_project(client, project_id):
    result = client.execute('''
    query {
      getProject(projectID: "%s") {
        id
      }
    }
    ''' % (project_id))
    return loads(result)['data']['getProject']
