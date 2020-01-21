import base64
import os
import re

from kili.authentication import KiliAuth
from kili.playground import Playground

email = input('Enter email: ')
password = getpass.getpass()
project_id = input('Enter project id: ')

kauth = KiliAuth(email=email,
                 password=password)
playground = Playground(kauth)


path_1 = os.path.join(os.getenv('HOME'),
                      'Downloads/1RpGWXY.png')
path_2 = os.path.join(os.getenv('HOME'),
                      'Downloads/trou-noir-espace-univers-astronomie.jpg')
filename_1 = os.path.basename(path_1)
filename_2 = os.path.basename(path_2)
playground.append_many_to_dataset(project_id=project_id,
                                  content_array=[path_1, path_2],
                                  external_id_array=[filename_1, filename_2])
