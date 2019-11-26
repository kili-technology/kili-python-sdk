from ..helper import format_result


def get_locks(client, project_id: str):
    result = client.execute('''
    query {
      getLocks(projectID: "%s") {
        id
        author {
          email
        }
        createdAt
        lockType
      }
    }
    ''' % (project_id))
    return format_result('getLocks', result)
