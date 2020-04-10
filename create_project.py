import os

from kili.authentication import KiliAuth
from kili.playground import Playground

email = os.getenv('KILI_EMAIL')
password = os.getenv('KILI_PASSWORD')
api_endpoint = 'https://cloud.kili-technology.com/api/label/graphql'

kauth = KiliAuth(email, password, api_endpoint)
playground = Playground(kauth)

title = 'Test'
description = 'Ceci est un projet test'
json_interface = {
    "filetype": "IMAGE",
    "jobs": {
        "JOB_0": {
            "mlTask": "OBJECT_DETECTION",
            "tools": ["rectangle"],
            "instruction": "Categories",
            "required": 1,
            "isChild": False,
            "content": {
                "categories": {
                    "OBJECT_A": {
                        "name": "Object A",
                        "children": ["JOB_1"]
                    },
                    "OBJECT_B": {
                        "name": "Object B",
                        "children": ["JOB_2"]
                    }
                },
                "input": "radio"
            }
        },
        "JOB_1": {
            "mlTask": "TRANSCRIPTION",
            "instruction": "Transcription of A",
            "required": 1,
            "isChild": True
        },
        "JOB_2": {
            "mlTask": "TRANSCRIPTION",
            "instruction": "Transcription of B",
            "required": 1,
            "isChild": True
        }
    }
}

user_id = playground.auth.user_id
project = playground.create_empty_project(user_id=user_id)
playground.update_properties_in_project(project_id=project['id'],
                                        title=title,
                                        description=description,
                                        json_interface=json_interface)

emails = ['collaborator1@kili-technology.com',
          'collaborator2@kili-technology.com']
for email in emails:
    playground.append_to_roles(
        project_id=project['id'], user_email=email, role='ADMIN')
