import datetime
import getpass
import json
import os

from kili.authentication import authenticate
from kili.queries.asset import export_assets
from tqdm import tqdm


email = input('Enter email: ')
password = getpass.getpass()
project_id = input('Enter project id: ')

client, user_id = authenticate(email, password)

assets = export_assets(client, project_id)


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
