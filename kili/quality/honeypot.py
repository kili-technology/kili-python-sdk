from ..helper import format_result


def create_honeypot(client, asset_id, json_response):
    result = client.execute('''
    mutation {
      createHoneypot(
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
    return format_result('createHoneypot', result)
