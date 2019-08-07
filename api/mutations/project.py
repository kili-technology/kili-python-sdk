from json import loads


def create_project(client, title, description, tool_type, use_honeypot, interface_json_settings):
    result = client.execute('''
    mutation {
      createProject(
      title: "%s",
      description: "%s",
      toolType: %s,
      useHoneyPot: %s,
      interfaceJsonSettings: "%s") {
        id
        title
        description
        author {
            id
            email
        }
        createdAt
        interfaceTools {
            name
            toolType
            jsonSettings
        }
        roles {
            user {
                id
                email
            }
            role
        }
        updatedAt
        useHoneyPot
      }
    }
    ''' % (title, description, tool_type, str(use_honeypot).lower(), interface_json_settings))
    return loads(result)['data']['createProject']


def delete_project(client, project_id):
    result = client.execute('''
    mutation {
      deleteProject(projectID: "%s") {
        id
      }
    }
    ''' % (project_id))
    return loads(result)['data']['deleteProject']


def append_to_roles(client, project_id, user_email, role):
    result = client.execute('''
    mutation {
      appendToRoles(
        projectID: "%s",
        userEmail: "%s",
        role: %s) {
          id
          title
          roles {
              user {
                id
                email
              }
              role
         }
      }
    }
    ''' % (project_id, user_email, role))
    return loads(result)['data']['appendToRoles']


def update_properties_in_project(client, project_id, min_consensus_size=None, consensus_tot_coverage=None):
    formatted_min_consensus_size = 'null' if min_consensus_size is None else int(min_consensus_size)
    formatted_consensus_tot_coverage = 'null' if consensus_tot_coverage is None else int(consensus_tot_coverage)

    result = client.execute('''
        mutation {
          updatePropertiesInProject(
            where: {id: "%s"},
            data: {
              minConsensusSize: %s
              consensusTotCoverage: %s
            }
          ) {
            id
          }
        }
        ''' % (project_id, formatted_min_consensus_size, formatted_consensus_tot_coverage))
    return loads(result)['data']['updatePropertiesInProject']
