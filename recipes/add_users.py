import getpass
from tqdm import tqdm
import yaml

from kili.authentication import KiliAuth
from kili.playground import Playground

from tqdm import tqdm


def get(dic, key):
    if key not in dic:
        return ''
    return dic[key]


email = input('Enter email: ')
password = getpass.getpass()
project_id = input('Enter project id: ')


with open('./conf/new_users.yml', 'r') as f:
    configuration = yaml.safe_load(f)

users = configuration['users']


DEFAULT_ORGANIZATION_ROLE = 'USER'


kauth = KiliAuth(email, password)
playground = Playground(kauth)

organization_id = playground.get_user(email=email)['organization']['id']

for user in tqdm(users):
    user_name = get(user, 'name')
    user_email = get(user, 'email')
    user_password = get(user, 'password')
    playground.create_user(name=user_name, email=user_email, password=user_password,
                           organization_id=organization_id, organization_role=DEFAULT_ORGANIZATION_ROLE)
    user_role = get(user, 'role')
    playground.append_to_roles(
        project_id=project_id, user_email=user_email, role=user_role)
