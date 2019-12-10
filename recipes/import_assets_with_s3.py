import base64
import getpass
import os
import random

import boto3
from kili.authentication import KiliAuth
from kili.playground import Playground

S3_ACCESS_KEY = os.getenv('S3_ACCESS_KEY')
S3_SECRET_KEY = os.getenv('S3_SECRET_KEY')
S3_ENDPOINT = os.getenv('S3_ENDPOINT')
S3_BUCKET = os.getenv('S3_BUCKET')


email = input('Enter email: ')
password = getpass.getpass()
project_id = input('Enter project id: ')

api_endpoint = 'https://cloud.kili-technology.com/api/label/graphql'
kauth = KiliAuth(email, password, api_endpoint)
playground = Playground(kauth)

s3_client = boto3.client(
    's3',
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    endpoint_url=S3_ENDPOINT,
    verify=False)

with open('./conf/new_assets_with_s3.yml', 'r') as f:
    configuration = yaml.safe_load(f)
assets = configuration['assets']

for asset in tqdm(assets):
    # Uploads asset to S3 bucket
    path = get(asset, 'path')
    key = str(random.getrandbits(128))
    s3_client.upload_file(path, S3_BUCKET, key)
    # Inserts asset with S3 key in Kili
    content = f'https://cloud.kili-technology.com/api/label/files?id={key}'
    external_id = get(asset, 'externalId')
    json_metadata = json.loads(get(asset, 'metadata'))
    project = playground.append_to_dataset(
        project_id=project_id, content=content, external_id=external_id)
