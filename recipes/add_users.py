import getpass
from tqdm import tqdm
import yaml

from kili.authentication import authenticate
from kili.mutations.user import create_user
from kili.mutations.project import append_to_roles
from kili.queries.user import get_user
from tqdm import tqdm


def get(dic, key):
    if key not in dic:
        return ''
    return dic[key]


email = input('Enter email: ')
password = getpass.getpass()
project_id = input('Enter project id: ')


with open('./new_users.yml', 'r') as f:
    configuration = yaml.safe_load(f)

users = configuration['users']


DEFAULT_ORGANIZATION_ROLE = 'USER'

client, user_id = authenticate(
    email, password, 'http://localhost:4000/graphql')

organization_id = get_user(client, email)['organization']['id']

for user in tqdm(users):
    user_name = get(user, 'name')
    user_email = get(user, 'email')
    user_password = get(user, 'password')
    user_phone = get(user, 'phone')
    create_user(client, user_name, user_email, user_password, user_phone,
                organization_id, DEFAULT_ORGANIZATION_ROLE)
    user_role = get(user, 'role')
    append_to_roles(
        client, project_id, user_email, user_role)
