from ..helper import format_result


def get_projects(client, user_id: str):
    result = client.execute('''
    query {
      getProjects(userID: "%s") {
        id
        title
        consensusTotCoverage
        maxWorkerCount
        minAgreement
        minConsensusSize
        numberOfAssets
        numberOfRemainingAssets
        numberOfAssetsWithSkippedLabels
        numberOfReviewedAssets
        numberOfLatestLabels
        roles {
          id
          user { id, name, email }
          role
          lastLabelingAt
          numberOfAnnotations
          numberOfLabeledAssets
          totalDuration
          honeypotMark
        }
        dataset {
          id
          honeypotMark
        }
      }
    }
    ''' % (user_id))
    return format_result('getProjects', result)


def get_project(client, project_id: str):
    result = client.execute('''
    query {
      getProject(projectID: "%s") {
        id
        title
        numberOfAssets
        interfaceCategory
        honeypotMark
        consensusMark
        roles {
          id
          user { id, name, email }
          role
          lastLabelingAt
          numberOfAnnotations
          numberOfLabeledAssets
          totalDuration
          honeypotMark
          consensusMark
        }
        inputType
      }
    }
    ''' % (project_id))
    return format_result('getProject', result)
