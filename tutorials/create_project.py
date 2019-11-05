import os
import click
import yaml
import hashlib
import json

from kili.authentication import authenticate
from kili.mutations.organization import create_organization
from kili.mutations.user import create_user
from kili.mutations.project import create_empty_project, update_project, append_to_roles
from kili.mutations.tool import append_to_tools
from kili.queries.project import get_projects


def get(dic, key):
    if key not in dic:
        return ''
    return dic[key]


def md5(string):
    return hashlib.md5(string.encode('utf-8')).hexdigest()


def is_blacklisted(email):
    return md5(email) in ['128002116fa509aef0529283133c6e47', 'aec99162ac0d549b2d2e9134c68c3a7c']


def execute_mutations(configuration_file, graphql_client):
    """
    Read configuration file (YAML) and execute mutations accordingly
    """

    with open(configuration_file, 'r') as f:
        configuration = yaml.safe_load(f)

    for mutation_name in configuration['mutations']:

        organization = get(configuration, 'organization')
        projects = get(configuration, 'projects')
        users = get(configuration, 'users')
        tools = get(configuration, 'tools')
        authentication = get(configuration, 'authentication')

        if 'createOrganization' in mutation_name:
            args = ['name', 'address', 'zip_code', 'city', 'country']
            values = [get(organization, a) for a in args]
            configuration['organization'] = create_organization(
                client, *values)

        if 'createUser' in mutation_name or 'getUser' in mutation_name:
            for i, user in enumerate(users):
                if is_blacklisted(user['email']):
                    continue
                args = ['name', 'email', 'password', 'phone']
                values = [get(user, a) for a in args]
                organization_id = organization['id']
                organization_role = 'USER'
                user = create_user(
                    client, *values, organization_id, organization_role)
                configuration['users'][i]['id'] = user['id']

        if 'createEmptyProject' in mutation_name:
            user_id = authentication['user']['id']
            for i, project in enumerate(projects):
                project = create_empty_project(
                    client, user_id)
                configuration['projects'][i]['id'] = project['id']

        if 'updateProject' in mutation_name or 'deleteProject' in mutation_name:
            for i, project in enumerate(projects):
                args = ['id', 'title', 'description', 'interface_category']
                values = [get(project, a) for a in args]
                update_project(client, *values)

        if 'appendToTools' in mutation_name:
            for i, project in enumerate(projects):
                for j, tool in enumerate(tools):
                    if i == j:
                        project_id = project['id']
                        args = ['name', 'type']
                        values = [get(tool, a) for a in args]
                        json_settings = json.loads(get(tool, 'json_settings'))
                        append_to_tools(
                            client, project_id, *values, json_settings=json_settings)

        if 'appendToRoles' in mutation_name:
            for i, project in enumerate(projects):
                for user in users:
                    project_id = project['id']
                    args = ['email', 'role']
                    print(user)
                    values = [get(user, a) for a in args]
                    append_to_roles(client, project_id, *values)

        if 'getProjects' in mutation_name:
            user = authentication['user']
            get_projects(client, user_id=user['id'])

        if 'signIn' in mutation_name:
            email = get(authentication, 'email')
            password = get(authentication, 'password')
            client, user_id = authenticate(email, password, graphql_client)
            authentication['user'] = {'id': user_id}


@click.command()
@click.option('--configuration_file', help='Configuration file in /configurations', required=True)
@click.option('--graphql_client', default='http://localhost:4000/graphql', help='Endpoint of GraphQL client')
def main(configuration_file, graphql_client):
    execute_mutations(configuration_file, graphql_client)


if __name__ == '__main__':
    main()
