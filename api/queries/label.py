from json import loads


def get_label(client, asset_id, user_id):
    result = client.execute('''
    query {
      getLabel(assetID: "%s", userID: "%s") {
        id
        jsonResponse
      }
    }
    ''' % (asset_id, user_id))
    return loads(result)['data']['getLabel']


def get_latest_labels_for_user(client, project_id, user_id):
    result = client.execute('''
    query {
      getLatestLabelsForUser(projectID: "%s", userID: "%s") {
        id
        jsonResponse
      }
    }
    ''' % (project_id, user_id))
    return loads(result)['data']['getLatestLabelsForUser']


def get_latest_labels(client, project_id, skip, first):
    result = client.execute('''
    query {
      getLatestLabels(projectID: "%s", skip: %d, first: %d) {
        id
        jsonResponse
      }
    }
    ''' % (project_id, skip, first))
    return loads(result)['data']['getLatestLabels']
