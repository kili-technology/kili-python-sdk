import getpass
from tqdm import tqdm
import yaml
import json

from kili.authentication import authenticate
from kili.mutations.asset import append_many_to_dataset
from tqdm import tqdm

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


client, user_id = authenticate(email, password)

for asset_chunk in tqdm(list(chunks(assets, CHUNK_SIZE))):
    external_id_array = [get(a, 'externalId') for a in asset_chunk]
    content_array = [get(a, 'content') for a in asset_chunk]
    json_metadata_array = [json.loads(get(a, 'metadata')) for a in asset_chunk]
    append_many_to_dataset(client, project_id, content_array,
                           external_id_array, json_metadata_array=json_metadata_array)
