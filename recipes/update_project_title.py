import click

from kili.client import Kili


@click.command()
@click.option('--api_endpoint', default='https://cloud.kili-technology.com/api/label/v2/graphql',
              help='Endpoint of GraphQL client')
def main(api_endpoint):
    api_key = input('Enter API KEY: ')
    project_id = input('Enter project id: ')
    title = input(
        'Enter a new title (leave blank and press [Enter] to leave title as is): ').strip()
    description = input(
        'Enter a new description (leave blank and press [Enter] to leave description as is): ').strip()

    kili = Kili(api_key=api_key, api_endpoint=api_endpoint)
    kili.update_properties_in_project(
        project_id=project_id, title=title, description=description)


if __name__ == '__main__':
    main()
