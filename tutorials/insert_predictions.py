import getpass
import hashlib
import json
import os
import tarfile
import urllib.request
from tqdm import tqdm

from google.cloud import language
from google.cloud.language import enums as language_enums
from google.protobuf.json_format import MessageToDict

from kili.authentication import authenticate
from kili.mutations.asset import append_to_dataset, update_properties_in_asset
from kili.mutations.label import create_prediction
from kili.queries.asset import get_assets_by_external_id


def download_dataset():
    url = 'https://www.cs.cmu.edu/~enron/enron_mail_20150507.tar.gz'
    filename = url.split('/')[-1]
    target_path = os.path.join('/tmp', filename)
    if not os.path.exists(target_path):
        print('downloading...')
        urllib.request.urlretrieve(url, target_path)
    return target_path


def extract_dataset(path):
    target_path = '/tmp/maildir'
    if not os.path.exists(target_path):
        tar = tarfile.open(path)
        tar.extractall(path='/tmp')
        tar.close()
    return target_path


def analyze_entities(text_content):
    client = language.LanguageServiceClient()
    type_ = language_enums.Document.Type.PLAIN_TEXT
    document = {"content": text_content, "type": type_}
    encoding_type = language_enums.EncodingType.UTF8
    response = client.analyze_entities(document, encoding_type=encoding_type)
    return MessageToDict(response)


def escape_content(str):
    return str.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\\$', "$")


def add_id_to_entities(entities):
    for entity in entities:
        for mention in entity['mentions']:
            key = '|'.join([entity['type'], mention['text']
                            ['content'], str(mention['text']['beginOffset'])])
            mention['id'] = hashlib.md5(key.encode()).hexdigest()
    return entities


email = input('Enter email: ')
password = getpass.getpass()
project_id = input('Enter project id: ')

MAX_NUMBER_OF_ASSET = 50

path_gz = download_dataset()
path_dir = extract_dataset(path_gz)

only_files = [os.path.join(path, name) for path,
              subdirs, files in os.walk(path_dir) for name in files]

client, user_id = authenticate(email, password)

for filepath in tqdm(only_files[:MAX_NUMBER_OF_ASSET]):
    with open(filepath, 'r') as f:
        content = f.read()
    external_id = filepath
    # Insert asset
    append_to_dataset(
        client, project_id, escape_content(content), external_id)
    asset = get_assets_by_external_id(client, project_id, external_id)
    asset_id = asset[0]['id']

    # Prioritize assets
    update_properties_in_asset(client, asset_id, priority=1)

    # Insert pre-annotations
    response = analyze_entities(content)
    entities = [e for e in response['entities']
                if isinstance(e['type'], str) and e['type'] != 'OTHER']
    json_response = {'entities': add_id_to_entities(entities)}
    create_prediction(client, asset_id, json_response)
