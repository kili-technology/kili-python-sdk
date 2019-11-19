from ..helper import format_result


def get_projects(client, user_id):
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
        completionPercentage
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
    return format_result('getProjects', result)


def get_project(client, project_id):
    result = client.execute('''
    query {
      getProject(projectID: "%s") {
        id
        interfaceCategory
        calculatedConsensusMark
        calculatedHoneypotMark
        consensusMark
        roles {
          id
          user { id, name, email }
          role
          lastLabelingAt
          numberOfAnnotations
          numberOfLabeledAssets
          totalDuration
          durationPerLabel
          honeypotMark
          calculatedConsensusMark
          calculatedHoneypotMark
          consensusMark
        }
      }
    }
    ''' % (project_id))
    return format_result('getProject', result)
