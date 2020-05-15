from kili.playground import Playground
from kili.authentication import KiliAuth
import os

pip install kili

email = os.getenv('KILI_USER_EMAIL')
password = os.getenv('KILI_USER_PASSWORD')
api_endpoint = os.getenv('KILI_API_ENDPOINT')

kauth = KiliAuth(email=email, password=password, api_endpoint=api_endpoint)
playground = Playground(kauth)
project_example = {
    'title': 'Car brand recognition',
    'description': 'Identify and locate cars',
    'input_type': 'IMAGE',
    'json_interface': {
        "filetype": "IMAGE",
        "jobs": {
            "JOB_0": {
                "mlTask": "OBJECT_DETECTION",
                "tools": [
                    "rectangle"
                ],
                "instruction": "What car brand ?",
                "required": 1,
                "isChild": False,
                "content": {
                    "categories": {
                        "TESLA": {"name": "Tesla"},
                        "FERRARI": {"name": "Ferrari"}
                    },
                    "input": "radio"
                }
            }
        }
    },

    'assets_to_import': [
        "https://images.caradisiac.com/logos/3/8/6/7/253867/S0-tesla-enregistre-d-importantes-pertes-au-premier-trimestre-175948.jpg",
        "https://img.sportauto.fr/news/2018/11/28/1533574/1920%7C1280%7Cc096243e5460db3e5e70c773.jpg"],

    'json_response': {
        "JOB_0": {
            "annotations": [{
                "boundingPoly": [{
                    "normalizedVertices": [
                        {"x": 0.16, "y": 0.82},
                        {"x": 0.16, "y": 0.32},
                        {"x": 0.82, "y": 0.32},
                        {"x": 0.82, "y": 0.82}
                    ]}
                ],
                "categories": [{"name": "TESLA", "confidence": 100}],
            }]
        }
    },
    'model_name': 'car-brand-localisation-v0.0.1'
}
project = playground.create_empty_project(user_id=playground.auth.user_id)
playground.update_properties_in_project(
    project_id=project['id'],
    title=project_example['title'],
    description=project_example['description'],
    input_type=project_example['input_type'],
    json_interface=project_example['json_interface'])
playground.append_many_to_dataset(
    project_id=project['id'],
    content_array=project_example['assets_to_import'],
    external_id_array=['ex1', 'ex2'])
playground.create_predictions(
    project_id=project['id'],
    external_id_array=['ex1'],
    model_name_array=[project_example['model_name']],
    json_response_array=[project_example['json_response']])
