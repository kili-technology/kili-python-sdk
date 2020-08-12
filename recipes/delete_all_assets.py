import getpass
import json

import yaml
from tqdm import tqdm

from kili.authentication import KiliAuth
from kili.playground import Playground

api_key = input('Enter API KEY: ')

kauth = KiliAuth(api_key=api_key)
playground = Playground(kauth)

assets = playground.assets(project_id=project_id)
asset_ids = [asset['id'] for asset in assets]
playground.delete_many_from_dataset(asset_ids=asset_ids)
