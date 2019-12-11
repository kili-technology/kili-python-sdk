import getpass
import json

import yaml
from tqdm import tqdm

from kili.authentication import KiliAuth
from kili.playground import Playground

email = input('Enter email: ')
password = getpass.getpass()
project_id = input('Enter project id: ')

kauth = KiliAuth(email=email, password=password)
playground = Playground(kauth)

assets = playground.get_assets(project_id=project_id)

for asset in tqdm(assets):
    playground.delete_from_dataset(asset_id=asset['id'])
