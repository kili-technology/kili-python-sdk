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


def kili_append_to_labels(client, author_id, is_review, json_response, label_asset_id, label_type,
                          milliseconds_to_label):
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
    ''' % (author_id, json_response, label_asset_id, label_type, milliseconds_to_label))
    return format_result('frontendAppendToLabels', result)
