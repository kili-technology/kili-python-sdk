from json import loads, dumps


def signin(client, email, password):
    result = client.execute('''
    mutation {
      signIn(email: "%s", password: "%s") {
        id
        token
        user {
          id
        }
      }
    }
    ''' % (email, password))
    return loads(result)['data']['signIn']


def kili_append_to_dataset(client, project_id, content, external_id, filename, is_instructions,
                           instructions, is_honeypot, consensus_mark, honeypot_mark, status):
    result = client.execute('''
    mutation {
      appendToDataset(projectID: "%s"
        content: "%s",
        externalID: "%s",
        filename: "%s",
        isInstructions: %s,
        instructions: "%s",
        isHoneypot: %s,
        consensusMark: %d,
        honeypotMark: %d,
        status: %s) {
        id
      }
    }
    ''' % (project_id, content, external_id, filename, str(is_instructions).lower(),
           instructions, str(is_honeypot).lower(), consensus_mark, honeypot_mark, status))
    return loads(result)['data']['appendToDataset']


def create_user(client, name, email, password, phone, organization_id, organization_role):
    result = client.execute('''
    mutation {
      createUser(name: "%s",
      email: "%s",
      password: "%s",
      phone: "%s",
      organizationID: "%s",
      organizationRole: %s) {
        id
      }
    }
    ''' % (name, email, password, phone, organization_id, organization_role))
    return loads(result)['data']['createUser']


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


def create_assets(client, project_id, contents, external_ids):
    result = client.execute('''
    mutation {
      createAssets(
        projectID: "%s",
        contents: %s,
        externalIDs: %s) {
          id
          content
          externalId
          createdAt
          updatedAt
          isHoneypot
          status
      }
    }
    ''' % (project_id, dumps(contents), dumps(external_ids)))
    return loads(result)['data']['createAssets']


def delete_assets_by_external_id(client, project_id, external_id):
    result = client.execute('''
    mutation {
      deleteAssetsByExternalId(projectID: "%s", externalID: "%s") {
        id
      }
    }
    ''' % (project_id, external_id))
    return loads(result)['data']['deleteAssetsByExternalId']


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
          millisecondsToLabel
          totalMillisecondsToLabel
          honeypotMark
      }
    }
    ''' % (asset_id, json_response))
    return loads(result)['data']['createPrediction']
