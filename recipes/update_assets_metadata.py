import getpass
import json

import click
import yaml
from tqdm import tqdm

from kili.authentication import KiliAuth
from kili.playground import Playground


def get(dic, key):
    if key not in dic:
        return ''
    return dic[key]


@click.command()
@click.option('--api_endpoint', default='https://cloud.kili-technology.com/api/label/graphql', help='Endpoint of GraphQL client')
def main(api_endpoint):
    email = input('Enter email: ')
    password = getpass.getpass()
    project_id = input('Enter project id: ')

    with open('./conf/new_assets.yml', 'r') as f:
        configuration = yaml.safe_load(f)

    assets = configuration['assets']

    kauth = KiliAuth(email=email, password=password, api_endpoint=api_endpoint)
    playground = Playground(kauth)

    for asset in tqdm(assets):
        external_id = get(asset, 'externalId')
        json_metadata = json.loads(get(asset, 'metadata'))
        assets = playground.get_assets_by_external_id(
            project_id=project_id, external_id=external_id)
        assert len(assets) == 1
        asset_id = assets[0]['id']
        playground.update_properties_in_asset(
            asset_id=asset_id, json_metadata=json_metadata)


if __name__ == '__main__':
    main()
