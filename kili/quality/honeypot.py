from ..helper import format_result, json_escape


def create_honeypot(client, asset_id: str, json_response: str):
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
    ''' % (asset_id, json_escape(json_response)))
    return format_result('createHoneypot', result)
