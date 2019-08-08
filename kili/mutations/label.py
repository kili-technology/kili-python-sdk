from ..helper import format_result


def create_prediction(client, asset_id, json_response):
    result = client.execute('''
    mutation {
      createPrediction(
        assetID: "%s",
        jsonResponse: "%s") {
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
    ''' % (asset_id, json_response))
    return format_result('createPrediction', result)


def append_to_labels(client, author_id, json_response, label_asset_id, label_type, seconds_to_label):
    result = client.execute('''
    mutation {
      appendToLabels(
        authorID: "%s",
        jsonResponse: "%s",
        labelAssetID: "%s",
        labelType: %s,
        secondsToLabel: %d) {
          id
      }
    }
    ''' % (author_id, json_response, label_asset_id, label_type, seconds_to_label))
    return format_result('appendToLabels', result)


def frontend_append_to_labels(client, author_id, json_response, label_asset_id, label_type, seconds_to_label):
    result = client.execute('''
    mutation {
      frontendAppendToLabels(
        authorID: "%s",
        jsonResponse: "%s",
        labelAssetID: "%s",
        labelType: %s,
        secondsToLabel: %d) {
          id
      }
    }
    ''' % (author_id, json_response, label_asset_id, label_type, seconds_to_label))
    return format_result('frontendAppendToLabels', result)


def update_label(client, label_id, label_asset_id, review_asset_id, author_id, label_type, json_response, seconds_to_label):
    result = client.execute('''
    mutation {
      updateLabel(
        labelID: "%s",
        labelAssetID: "%s",
        reviewAssetID: "%s",
        authorID: "%s",
        labelType: %s,
        jsonResponse: "%s",
        secondsToLabel: %d) {
          id
      }
    }
    ''' % (label_id, label_asset_id, review_asset_id, author_id, label_type, json_response, seconds_to_label))
    return format_result('updateLabel', result)
