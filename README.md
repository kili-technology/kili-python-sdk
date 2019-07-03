# kili-playground

## Execute mutations

You have two ways for interacting with Kili's API :

- Either execute a predefined sequence of mutations/queries using `scripts_playground/execute_mutation.py`
- Or execute a custom mutation/query with Python's `graphqlclient`

### Execute a predefined sequence of mutations/queries

We already implemented several sequences in order to:
 
1. `scripts_playground_playground/configurations/add_new_project.yml`:
  - Create the given organization
  - Create all given users within this organization
  - Create an empty project according to given properties

2. `configurations/delete_project.yml`:
  - Delete a project according to a given ID
  
3. `Kili's example notebook`:
  - Add asset to project
  - Download Assets 
  - Add Label to assets  

You can modify the content of the configurations to serve your needs:

- update configuration properties
- update sequence of mutations

Then launch:

```bash
cd scripts_playground
pip install -r requirements.txt
python execute_mutations.py --configuration_file configurations/CHOSEN_CONFIGURATION --graphql_client https://cloud.kili-technology.com/api/label/graphql
```



### Execute custom mutations/queries

Kili's API secures all queries and mutations with [JWT tokens](https://en.wikipedia.org/wiki/JSON_Web_Token).

If you decide to use Python's GraphQL you need to:

- Authenticate via the `signIn` resolver, in order to retrieve the authentication token

```python
from graphqlclient import GraphQLClient
import json

graphql_client = GraphQLClient("https://cloud.kili-technology.com/api/label/graphql")

sign_in = json.loads(graphql_client.execute('''mutation {
    signIn(
        email: "MY_EMAIL",
        password: "MY_PASSWORD"
    ) {
       id
        token
    }
}'''))
```

- Retrieve the token and inject it in the GraphQL client

```python
token = sign_in['data']['signIn']['token']
graphql_client.inject_token(f'Bearer: {token}')
```

- Launch the desired mutation/query
````python
graphql_client.execute('''
    mutation {
    	updateProject(
    		projectID: "PROJECT_ID"
    		title: "NEW_PROJECT_TITLE"
    	)
    	{
    	  id
        }
    }
''')
````


