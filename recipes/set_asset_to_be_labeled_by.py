import getpass

import click
import yaml
from tqdm import tqdm

from kili.authentication import KiliAuth
from kili.playground import Playground


def get(dic, key):
    if key not in dic:
        return ''
    return dic[key]


def get_asset_by_external_id(playground, project_id, external_id):
    assets = playground.get_assets_by_external_id(
        project_id=project_id, external_id=external_id)
    assert len(assets) == 1
    return assets[0]


@click.command()
@click.option('--api_endpoint', default='https://cloud.kili-technology.com/api/label/graphql', help='Endpoint of GraphQL client')
def main(api_endpoint):
    email = input('Enter email: ')
    password = getpass.getpass()
    project_id = input('Enter project id: ')

    with open('./conf/new_assets.yml', 'r') as f:
        configuration = yaml.safe_load(f)

    assets = configuration['assets']

    kauth = KiliAuth(email, password, api_endpoint)
    playground = Playground(kauth)

    project = playground.get_project(project_id=project_id)
    roles = get(project, 'roles')

    for asset in tqdm(assets):
        external_id = get(asset, 'externalId')
        to_be_labeled_by = [get(user, 'email')
                            for user in get(asset, 'toBeLabeledBy')]
        asset = get_asset_by_external_id(playground, project_id, external_id)
        asset_id = get(asset, 'id')
        playground.update_properties_in_asset(
            asset_id=asset_id, to_be_labeled_by=to_be_labeled_by)


if __name__ == '__main__':
    main()
