import getpass
from tqdm import tqdm
import yaml
import json

from kili.authentication import authenticate
from kili.mutations.asset import delete_from_dataset
from kili.queries.asset import export_assets
from tqdm import tqdm


email = input('Enter email: ')
password = getpass.getpass()
project_id = input('Enter project id: ')


client, user_id = authenticate(email, password)

assets = export_assets(client, project_id)

for asset in tqdm(assets):
    delete_from_dataset(client, asset['id'])
