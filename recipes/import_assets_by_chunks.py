import getpass
import json

import yaml
from tqdm import tqdm

from kili.authentication import KiliAuth
from kili.playground import Playground

CHUNK_SIZE = 100


def get(dic, key):
    if key not in dic:
        return ''
    return dic[key]


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


email = input('Enter email: ')
password = getpass.getpass()
project_id = input('Enter project id: ')

with open('./conf/new_assets.yml', 'r') as f:
    configuration = yaml.safe_load(f)

assets = configuration['assets']

kauth = KiliAuth(email=email, password=password)
playground = Playground(kauth)

for asset_chunk in tqdm(list(chunks(assets, CHUNK_SIZE))):
    external_id_array = [get(a, 'externalId') for a in asset_chunk]
    content_array = [get(a, 'content') for a in asset_chunk]
    json_metadata_array = [json.loads(get(a, 'metadata')) for a in asset_chunk]
    playground.append_many_to_dataset(project_id=project_id, content_array=content_array,
                                      external_id_array=external_id_array, json_metadata_array=json_metadata_array)
