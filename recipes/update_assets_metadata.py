import getpass
from tqdm import tqdm
import yaml
import json
import click

from kili.authentication import authenticate
from kili.mutations.asset import update_properties_in_asset
from kili.queries.asset import get_assets_by_external_id
from tqdm import tqdm


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

    client, user_id = authenticate(email, password, api_endpoint)

    for asset in tqdm(assets):
        external_id = get(asset, 'externalId')
        json_metadata = json.loads(get(asset, 'metadata'))
        assets = get_assets_by_external_id(client, project_id, external_id)
        assert len(assets) == 1
        asset_id = assets[0]['id']
        update_properties_in_asset(
            client, asset_id, json_metadata=json_metadata)


if __name__ == '__main__':
    main()
