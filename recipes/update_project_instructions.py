import getpass

import click

from kili.authentication import KiliAuth
from kili.playground import Playground


@click.command()
@click.option('--api_endpoint', default='https://cloud.kili-technology.com/api/label/graphql',
              help='Endpoint of GraphQL client')
def main(api_endpoint):
    email = input('Enter email: ')
    password = getpass.getpass()
    project_id = input('Enter project id: ')
    instructions = input('Enter link to instructions (leave blank and press [Enter] to disable instructions): ').strip()

    if not instructions.startswith('http') and not instructions == '':
        raise Exception('The link to instructions should be an URL beginning in http:// or https://')

    kauth = KiliAuth(email, password, api_endpoint=api_endpoint)
    playground = Playground(kauth)
    playground.update_properties_in_project(project_id=project_id, instructions=instructions)


if __name__ == '__main__':
    main()
