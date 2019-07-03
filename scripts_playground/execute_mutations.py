import json
import os

import click
import yaml
from graphqlclient import GraphQLClient
from jinja2 import Environment, FileSystemLoader


class GraphQLError(Exception):
    def __init__(self, mutation, error):
        super().__init__(f'Mutation {mutation} failed with error: {error}')


def send_mutation_to_graphql(mutation, graphql_client):
    try:
        result = graphql_client.execute(mutation)
        json_result = json.loads(result)
        if 'errors' in json_result:
            raise GraphQLError(mutation, json_result['errors'])

        print(f'Mutation {mutation} succeeded with result: {result}')
        return json_result

    except Exception as error:
        raise GraphQLError(mutation, error)


def get(dic, key):
    if key not in dic:
        return ''

    return dic[key]


def render_mutation(mutation_template, authentication={}, organization={}, project={}, tool={}, user={}):
    return mutation_template.render(authentication_email=get(authentication, 'email'),
                                    authentication_id=get(authentication, 'id'),
                                    authentication_password=get(authentication, 'password'),
                                    organization_address=get(organization, 'address'),
                                    organization_city=get(organization, 'city'),
                                    organization_country=get(organization, 'country'),
                                    organization_id=get(organization, 'id'),
                                    organization_name=get(organization, 'name'),
                                    organization_zip_code=get(organization, 'zip_code'),
                                    project_description=get(project, 'description'),
                                    project_id=get(project, 'id'),
                                    project_interface_category=get(project, 'interface_category'),
                                    project_title=get(project, 'title'),
                                    tool_json_settings=get(tool, 'json_settings'),
                                    tool_name=get(tool, 'name'),
                                    tool_type=get(tool, 'type'),
                                    user_email=get(user, 'email'),
                                    user_id=get(user, 'id'),
                                    user_name=get(user, 'name'))


def execute_mutations(configuration_file, graphql_client):
    """
    Read configuration file (YAML) and execute mutations accordingly
    """
    client = GraphQLClient(graphql_client)
    current_directory = os.path.dirname(os.path.abspath(__file__))
    jinja2 = Environment(loader=FileSystemLoader(current_directory))

    with open(configuration_file, 'r') as f:
        configuration = yaml.safe_load(f)

    for mutation_name in configuration['mutations']:
        mutation_template = jinja2.get_template(f'mutations/{mutation_name}.graphql')

        organization = get(configuration, 'organization')
        project = get(configuration, 'project')
        users = get(configuration, 'users')
        tools = get(configuration, 'tools')
        authentication = get(configuration, 'authentication')

        if 'createOrganization' in mutation_name:
            mutation = render_mutation(mutation_template, organization=organization)
            organization_result = send_mutation_to_graphql(mutation, client)
            organization_id = organization_result['data']['createOrganization']['id']
            configuration['organization']['id'] = organization_id

        if 'createUser' in mutation_name or 'getUser' in mutation_name:
            for i, user in enumerate(users):
                mutation = render_mutation(mutation_template, organization=organization, user=user)
                user_result = send_mutation_to_graphql(mutation, client)
                user_id = user_result['data']['createUser']['id']
                configuration['users'][i]['id'] = user_id

        if 'createProject' in mutation_name:
            mutation = render_mutation(mutation_template)
            project_result = send_mutation_to_graphql(mutation, client)
            project_id = project_result['data']['createProject']['id']
            configuration['project']['id'] = project_id

        if 'updateProject' in mutation_name or 'deleteProject' in mutation_name:
            mutation = render_mutation(mutation_template, project=project)
            send_mutation_to_graphql(mutation, client)

        if 'appendToTools' in mutation_name:
            for tool in tools:
                mutation = render_mutation(mutation_template, tool=tool, project=project)
                send_mutation_to_graphql(mutation, client)

        if 'appendToRoles' in mutation_name:
            for user in users:
                mutation = render_mutation(mutation_template, user=user, project=project)
                send_mutation_to_graphql(mutation, client)

        if 'getProjects' in mutation_name:
            user = authentication['user']
            mutation = render_mutation(mutation_template, user=user)
            projects_result = send_mutation_to_graphql(mutation, client)
            configuration['projects'] = projects_result['data']['getProjects']

        if 'forceProjectKpiComputation' in mutation_name:
            for project in configuration['projects']:
                mutation = render_mutation(mutation_template, project=project)
                send_mutation_to_graphql(mutation, client)

        if 'signIn' in mutation_name:
            mutation = render_mutation(mutation_template, authentication=authentication)
            authentication_result = send_mutation_to_graphql(mutation, client)
            current_user = authentication_result['data']['signIn']
            token = current_user['token']
            configuration['authentication'] = current_user
            client.inject_token(f'Bearer: {token}')


@click.command()
@click.option('--configuration_file', help='Configuration file in /configurations', required=True)
@click.option('--graphql_client', default='http://localhost:4000/graphql', help='Endpoint of GraphQL client')
def main(configuration_file, graphql_client):
    execute_mutations(configuration_file, graphql_client)


if __name__ == '__main__':
    main()
