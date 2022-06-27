from tqdm import tqdm
import os
import yaml

from kili.client import Kili

from tqdm import tqdm


def get(dic, key):
    if key not in dic:
        return ''
    return dic[key]


project_id = input('Enter project id: ')


with open('./conf/new_users.yml', 'r') as f:
    configuration = yaml.safe_load(f)

users = configuration['users']


DEFAULT_ORGANIZATION_ROLE = 'USER'

# If you use Kili SaaS, use the url 'https://cloud.kili-technology.com/api/label/v2/graphql'
api_endpoint = os.getenv('KILI_API_ENDPOINT')

kili = Kili(api_endpoint=api_endpoint)

for user in tqdm(users):
    user_firstname = get(user, 'firstname')
    user_lastname = get(user, 'lastname')
    user_email = get(user, 'email')
    user_password = get(user, 'password')
    kili.create_user(firstname=user_firstname, lastname=user_lastname, email=user_email,
                     password=user_password, organization_role=DEFAULT_ORGANIZATION_ROLE)
    user_role = get(user, 'role')
    kili.append_to_roles(
        project_id=project_id, user_email=user_email, role=user_role)
