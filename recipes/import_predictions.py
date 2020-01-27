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

    external_id_array = [get(prediction, 'externalId')
                         for prediction in predictions]
    model_name_array = [get(prediction, 'modelName')
                        for prediction in predictions]
    json_response_array = [json.loads(
        get(prediction, 'response')) for prediction in predictions]
    playground.create_predictions(
        project_id=project_id,
        external_id_array=external_id_array,
        model_name_array=model_name_array,
        json_response_array=json_response_array)


if __name__ == '__main__':
    main()
