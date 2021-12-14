import os

from kili.client import Kili

api_key = os.getenv('KILI_USER_API_KEY')
# If you use Kili SaaS, use the url 'https://cloud.kili-technology.com/api/label/v2/graphql'
api_endpoint = os.getenv('KILI_API_ENDPOINT')

kili = Kili(api_key=api_key, api_endpoint=api_endpoint)

project_id = input('Enter project id: ')

assets = kili.assets(project_id=project_id)
asset_ids = [asset['id'] for asset in assets]
kili.delete_many_from_dataset(asset_ids=asset_ids)
