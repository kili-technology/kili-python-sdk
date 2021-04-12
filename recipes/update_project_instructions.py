import getpass

import click

from kili.client import Kili


@click.command()
@click.option('--api_endpoint', default='https://cloud.kili-technology.com/api/label/v2/graphql',
              help='Endpoint of GraphQL client')
def main(api_endpoint):
    api_key = input('Enter API KEY: ')
    project_id = input('Enter project id: ')
    instructions = input(
        'Enter link to instructions (leave blank and press [Enter] to disable instructions): ').strip()

    if not instructions.startswith('http') and not instructions == '':
        raise Exception(
            'The link to instructions should be an URL beginning in http:// or https://')

    kili = Kili(api_key=api_key, api_endpoint=api_endpoint)
    kili.update_properties_in_project(
        project_id=project_id, instructions=instructions)


if __name__ == '__main__':
    main()
