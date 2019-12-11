import getpass
import hashlib
import json

import click
import yaml
from tqdm import tqdm

from kili.authentication import KiliAuth, authenticate
from kili.mutations.organization import create_organization
from kili.mutations.project import (append_to_roles, create_empty_project,
                                    update_project)
from kili.mutations.tool import append_to_tools
from kili.mutations.user import create_user
from kili.playground import Playground
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

    for mutation_name in tqdm(configuration['mutations']):

        organization = get(configuration, 'organization')
        projects = get(configuration, 'projects')
        users = get(configuration, 'users')
        tools = get(configuration, 'tools')
        authentication = get(configuration, 'authentication')

        if 'createOrganization' in mutation_name:
            if 'id' in organization:
                configuration['organization'] = organization
                continue
            configuration['organization'] = playground.create_organization(
                name=get(organization, 'name'),
                address=get(organization, 'address'),
                zip_code=get(organization, 'zip_code'),
                city=get(organization, 'city'),
                country=get(organization, 'country'))

        if 'createUser' in mutation_name or 'getUser' in mutation_name:
            for i, user in enumerate(users):
                if is_blacklisted(user['email']):
                    continue
                user = playground.create_user(
                    name=get(user, 'name'),
                    email=get(user, 'email'),
                    password=get(user, 'password'),
                    phone=get(user, 'phone'),
                    organization_id=organization['id'],
                    organization_role='USER')
                configuration['users'][i]['id'] = user['id']

        if 'createEmptyProject' in mutation_name:
            user_id = authentication['user']['id']
            for i, project in enumerate(projects):
                project = playground.create_empty_project(
                    user_id=user_id)
                configuration['projects'][i]['id'] = project['id']

        if 'updateProject' in mutation_name or 'deleteProject' in mutation_name:
            for i, project in enumerate(projects):
                playground.update_project(
                    project_id=get(project, 'id'),
                    title=get(project, 'title'),
                    description=get(project, 'description'),
                    interface_category=get(project, 'interface_category'))

        if 'appendToTools' in mutation_name:
            for i, project in enumerate(projects):
                for j, tool in enumerate(tools):
                    if i == j:
                        project_id = project['id']
                        json_settings = json.loads(get(tool, 'json_settings'))
                        playground.append_to_tools(
                            project_id=project_id,
                            name=get(tool, 'name'),
                            type=get(tool, 'type'),
                            json_settings=json_settings)

        if 'appendToRoles' in mutation_name:
            for i, project in enumerate(projects):
                for user in users:
                    project_id = project['id']
                    playground.append_to_roles(project_id=project_id,
                                               email=get(user, 'email'),
                                               role=get(user, 'role'))

        if 'getProjects' in mutation_name:
            user = authentication['user']
            playground.get_projects(user_id=user['id'])

        if 'signIn' in mutation_name:
            email = get(authentication, 'email')
            password = getpass.getpass(f'Enter password for user "{email}":')
            kauth = KiliAuth(email=email, password=password,
                             api_endpoint=graphql_client)
            playground = Playground(kauth)
            authentication['user'] = {'id': kauth.user_id}


@click.command()
@click.option('--configuration_file', help='Configuration file in /configurations', required=True)
@click.option('--graphql_client', default='http://localhost:4000/graphql', help='Endpoint of GraphQL client')
def main(configuration_file, graphql_client):
    execute_mutations(configuration_file, graphql_client)


if __name__ == '__main__':
    main()
