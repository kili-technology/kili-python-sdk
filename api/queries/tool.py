from json import loads


def get_tools(client, project_id):
    result = client.execute('''
    query {
      getTools(projectID: "%s") {
        id
      }
    }
    ''' % (project_id))
    return loads(result)['data']['getTools']
