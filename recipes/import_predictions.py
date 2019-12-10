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

    with open('./conf/new_predictions.yml', 'r') as f:
        configuration = yaml.safe_load(f)

    predictions = configuration['predictions']

    kauth = KiliAuth(email=email, password=password, api_endpoint=api_endpoint)
    playground = Playground(kauth)

    for prediction in tqdm(predictions):
        external_id = get(prediction, 'externalId')
        assets = playground.get_assets_by_external_id(
            project_id=project_id, external_id=external_id)
        assert len(assets) == 1
        asset_id = assets[0]['id']
        json_response = json.loads(get(prediction, 'response'))
        playground.create_prediction(
            asset_id=asset_id, json_response=json_response)


if __name__ == '__main__':
    main()
