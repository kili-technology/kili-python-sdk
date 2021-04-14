import getpass
import json

import yaml
from tqdm import tqdm

from kili.client import Kili

api_key = input('Enter API KEY: ')

kili = Kili(api_key=api_key)

assets = kili.assets(project_id=project_id)
asset_ids = [asset['id'] for asset in assets]
kili.delete_many_from_dataset(asset_ids=asset_ids)
