from json import loads


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
          millisecondsToLabel
          totalMillisecondsToLabel
          honeypotMark
      }
    }
    ''' % (asset_id, json_response))
    return loads(result)['data']['createHoneypot']
