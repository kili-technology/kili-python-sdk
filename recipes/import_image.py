import base64
import os
import re

from kili.authentication import KiliAuth
from kili.playground import Playground

email = input('Enter email: ')
password = getpass.getpass()
project_id = input('Enter project id: ')
image_path = input('Enter image path: ')

kauth = KiliAuth(email=email,
                 password=password)
playground = Playground(kauth)

filename = os.path.basename(image_path)
playground.append_many_to_dataset(project_id=project_id,
                                  content_array=[image_path],
                                  external_id_array=[filename])
