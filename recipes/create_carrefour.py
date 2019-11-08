import argparse
import getpass
import json
import os
import uuid

import pandas as pd
from kili.authentication import authenticate
from kili.mutations.asset import append_to_dataset
from kili.mutations.label import append_to_labels
from kili.queries.asset import get_assets, get_assets_by_external_id
from kili.queries.project import get_projects
from tqdm import tqdm


def get_asset_by_external_id(client, project_id, external_id):
    assets = get_assets(client, project_id, skip=0, first=50000)
    if assets:
        assets = list(
            filter(lambda a: a and a['externalId'] == external_id, assets))
        if assets:
            return assets[0]


def append_asset_to_kili(client, project_id, filename, content, external_id):
    asset = get_asset_by_external_id(client, project_id, external_id)
    return asset


def format_yumain_to_kili(yumain_response):
    annotations = []
    for a in yumain_response['localizedObjectAnnotations']:
        vertices = a['boundingPoly']['normalizedVertices']
        annotations.append({
            'id': uuid.uuid4().hex,
            'score': 100,
            'description': [{a['name']: 100}],
            'isOccluded': False,
            'isCut': False,
            'boundingPoly': [{'normalizedVertices': [{'x': v['x'], 'y': v['y']} for v in vertices]}]
        })
    kili_response = {'annotations': annotations}
    return kili_response


def insert_assets(dataset, path, project_name):
    df = pd.read_csv(
        f'{path}/merged_baskets_images_with_metadata_{project_name}.csv', sep=";")
    for index, row in tqdm(list(df.iterrows())):
        external_id = row['externalId']
        metadata = row['metadata']
        if len(metadata) < 5:
            print("Metadata is too small for: ", external_id, metadata)
        #external_id = f'{dataset}-{index}'
        assets = get_assets_by_external_id(client, project_id, external_id)
        if assets is None:
            print("Inserting : ", external_id)
            url = row['url']
            asset = append_to_dataset(client, project_id, url, external_id, external_id,
                                      is_instructions=False,
                                      instructions='',
                                      is_honeypot=False,
                                      consensus_mark=0,
                                      honeypot_mark=0,
                                      status='TODO',
                                      json_metadata=json.loads(metadata))


def insert_labels(dataset, path):
    df = pd.read_csv(f'{path}/yumain-{dataset}.csv')
    for index, row in tqdm(list(df.iterrows())):
        filename = row['name']
        external_id = f'{dataset}-{index}'
        assets = get_assets_by_external_id(client, project_id, external_id)
        assert len(assets) == 1
        asset = assets[0]

        # Reads Yumain annotations
        filename_base, _ = os.path.splitext(filename)
        label_path = os.path.join(
            os.getenv('HOME'), 'Downloads', 'GOOGLEVISION', f'{filename_base}.json')
        if not os.path.exists(label_path):
            continue
        with open(label_path, 'r') as f:
            data = json.loads(f.read())
        assert len(data['responses']) == 1

        # Format
        yumain_response = data['responses'][0]
        json_response = format_yumain_to_kili(yumain_response)

        is_review = False
        label = append_to_labels(client, user_id, is_review, json_response,
                                 asset['id'], label_type='PREDICTION', milliseconds_to_label=0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import assets and labels')
    parser.add_argument('-m', dest="mode", type=str)
    parser.add_argument('-a', dest="api_endpoint", type=str)
    parser.add_argument('-p', dest="path", type=str)
    args = parser.parse_args()

    email = 'emeric.creuse@puredatasource.io'
    password = getpass.getpass('Enter your password:')

    # Authenticate

    client, user_id = authenticate(email, password, args.api_endpoint)

    # Get project

    projects = get_projects(client, user_id)
    project_title = args.path.split("/")[-1]
    second_project_title = args.path.split("/")[-2]

    if project_title == "italy" or second_project_title == "italy":
        project_name = "ITALY"
        project = next(filter(
            lambda p: p['title'] == 'Italy - Products annotation in basket', projects))
    elif project_title == "valenciennes" or second_project_title == "valenciennes":
        project_name = "VALENCIENNES"
        project = next(filter(
            lambda p: p['title'] == 'Valenciennes - Products annotation in basket', projects))
    else:
        raise NameError('Path misspelled')

    project_id = project['id']

    # Insert assets

    if args.mode == 'assets':
        # for dataset in ['train', 'val']:
        for dataset in ['train']:
            insert_assets(dataset, args.path, project_name)
            pass

    # Insert labels

    if args.mode == 'labels':
        # for dataset in ['train', 'val']:
        for dataset in ['train']:
            insert_labels(dataset, args.path)
