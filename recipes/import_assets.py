import getpass
import json

import yaml
from tqdm import tqdm

from kili.authentication import KiliAuth
from kili.playground import Playground


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

kauth = KiliAuth(email=email, password=password)
playground = Playground(kauth)

for asset in tqdm(assets):
    external_id = get(asset, 'externalId')
    content = get(asset, 'content')
    json_metadata = json.loads(get(asset, 'metadata'))
    playground.append_to_dataset(project_id=project_id, content=content,
                                 external_id=external_id, json_metadata=json_metadata)
