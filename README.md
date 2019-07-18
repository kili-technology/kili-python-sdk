# Kili Playground

## Installation

```bash
git clone https://github.com/kili-technology/kili-playground.git
cd kili-playground
```

## Get started

### Authenticate

In python:

```python
from graphqlclient import GraphQLClient
import json

def authenticate(email, password):
    client = GraphQLClient('https://cloud.kili-technology.com/api/label/graphql')
    auth_payload = signin(client, email, password)
    api_token = auth_payload['token']
    client.inject_token('Bearer: ' + api_token)
    user_id = auth_payload['user']['id']
    return client, user_id

client, user_id = authenticate('MY_EMAIL', 'MY_ADDRESS')
```

### Data modifications (mutations)

```python
from helpers.mutations import *

client, _ = authenticate('MY_EMAIL', 'MY_ADDRESS')
```

| Action                                  | Function signature                                                                              |
| --------------------------------------- | ----------------------------------------------------------------------------------------------- |
|  Create a user                          |  `create_user(client, name, email, password, phone, organization_id, organization_role)`        |
|  Create a project                       |  `create_project(client, title, description, tool_type, use_honeypot, interface_json_settings)` |
|  Delete a project                       |  `delete_project(client, project_id)`                                                           |
|  Append a user to a project             |  `append_to_roles(client, project_id, user_email, role)`                                        |
|  Create a bulk of assets (image, text)  |  `create_assets(client, project_id, contents, external_ids)`                                    |
|  Delete assets                          |  `delete_assets_by_external_id(client, project_id, external_id)`                                |
|  Turn an asset into a honeypot          |  `create_honeypot(client, asset_id, json_response)`                                             |
|  Push a prediction to be labeled        |  `create_prediction(client, asset_id, json_response)`                                           |

### Data queries

| Action                         | Function signature                                            |
| ------------------------------ | ------------------------------------------------------------- |
|  Get the list of my projects   |  `get_projects(client, user_id)`                              |
|  Get a specific asset          |  `get_assets_by_external_id(client, project_id, external_id)` |
|  Export all assets and labels  |  `export_assets(client, project_id)`                          |
