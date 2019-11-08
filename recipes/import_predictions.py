import getpass
from tqdm import tqdm
import yaml
import json

from kili.authentication import authenticate
from kili.mutations.label import create_prediction
from kili.queries.asset import get_assets_by_external_id
from tqdm import tqdm


def get(dic, key):
    if key not in dic:
        return ''
    return dic[key]


email = input('Enter email: ')
password = getpass.getpass()
project_id = input('Enter project id: ')


with open('./conf/new_predictions.yml', 'r') as f:
    configuration = yaml.safe_load(f)

predictions = configuration['predictions']


client, user_id = authenticate(email, password)

for prediction in tqdm(predictions):
    external_id = get(prediction, 'externalId')
    assets = get_assets_by_external_id(client, project_id, external_id)
    assert len(assets) == 1
    asset_id = assets[0]['id']
    json_response = json.loads(get(prediction, 'response'))
    create_prediction(client, asset_id, json_response)
