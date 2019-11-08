import getpass
from tqdm import tqdm
import yaml
import json

from kili.authentication import authenticate
from kili.mutations.asset import append_to_dataset
from tqdm import tqdm


def get(dic, key):
    if key not in dic:
        return ''
    return dic[key]


email = input('Enter email: ')
password = getpass.getpass()
project_id = input('Enter project id: ')

with open('./conf/new_assets.yml', 'r') as f:
    configuration = yaml.safe_load(f)

assets = configuration['assets']


client, user_id = authenticate(email, password)

for asset in tqdm(assets):
    external_id = get(asset, 'externalId')
    content = get(asset, 'content')
    json_metadata = json.loads(get(asset, 'metadata'))
    append_to_dataset(client, project_id, content,
                      external_id, json_metadata=json_metadata)
