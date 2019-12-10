import datetime
import getpass
import json
import os

from tqdm import tqdm

from kili.authentication import KiliAuth
from kili.playground import Playground

email = input('Enter email: ')
password = getpass.getpass()
project_id = input('Enter project id: ')

kauth = KiliAuth(email=email, password=password)
playground = Playground(kauth)

assets = playground.get_assets(project_id=project_id)


NOT_USED_FIELDS = ['content', 'createdAt',
                   'updatedAt', 'isHoneypot', 'isInstructions', 'status', 'labels']


def is_reviewed(asset):
    return 'REVIEW' in [l['labelType'] for l in asset['labels']]


# Get more recent Review if any, otherwise most recent Label

for asset in tqdm(assets):
    sorted_labels = sorted(asset['labels'],
                           key=lambda l: l['createdAt'], reverse=True)
    if is_reviewed(asset):
        sorted_labels = [
            l for l in sorted_labels if l['labelType'] == 'REVIEW']
    last_label = sorted_labels[0]
    asset['label'] = json.loads(last_label['jsonResponse'])
    asset['labelType'] = last_label['labelType']
    for key in NOT_USED_FIELDS:
        asset.pop(key, None)

# Print the first 3 labels

print(assets[:3])
