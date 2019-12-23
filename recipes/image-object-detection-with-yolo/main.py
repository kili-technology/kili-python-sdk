import json
import os
import random
import subprocess
from tempfile import TemporaryDirectory

import requests
from PIL import Image

from kili.transfer_learning import TransferLearning

EMAIL = os.environ['EMAIL']
PASSWORD = os.environ['PASSWORD']
PROJECT_ID = os.environ['PROJECT_ID']
API_ENDPOINT = os.environ['API_ENDPOINT']
PYTHONPATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'yolov3')

COCO_NAMES_FILE = 'data/coco.names'
COCO_TRAIN_TEST_TXT_FILE = 'data/coco.txt'
COCO_DATA_FILE = 'data/coco.data'
COCO_DATA_FILE_TEMPLATE = 'data/coco.template.data'
CONFIG_FILE = 'cfg/yolov3.cfg'
CONFIG_FILE_TEMPLATE = 'cfg/yolov3.template.cfg'
WEIGHTS_FILE = 'weights/yolov3.pt'
BEST_WEIGHTS_FILE = 'weights/best.pt'
LAST_WEIGHTS_FILE = 'weights/last.pt'

# TODO: Give the possibility to predict only with YOLO weights without training

os.chdir(PYTHONPATH)


def convert_from_yolo_to_kili_format(x1, y1, x2, y2, category, score, total_width, total_height):
    annotations = {'score': float(score),
                   'description': [{}],
                   'boundingPoly': [
                       {'normalizedVertices': [
                           {'x': x1 / total_width, 'y': y1 / total_height},
                           {'x': x2 / total_width, 'y': y1 / total_height},
                           {'x': x1 / total_width, 'y': y2 / total_height},
                           {'x': x2 / total_width, 'y': y2 / total_height},
                       ]}
                   ],
                   'type': 'RECTANGLE'}
    annotations['description'][0][str(category)] = int(float(score) * 100)

    return annotations


def convert_from_kili_to_yolo_format(label):
    if 'jsonResponse' not in label:
        return []
    import json
    json_response = json.loads(label['jsonResponse'])
    if 'annotations' not in json_response:
        return []
    annotations = json_response['annotations']
    converted_annotations = []
    for annotation in annotations:
        category = list(annotation['description'][0].keys())[0]
        if 'boundingPoly' not in annotation:
            continue
        bounding_poly = annotation['boundingPoly']
        if len(bounding_poly) < 1:
            continue
        if 'normalizedVertices' not in bounding_poly[0]:
            continue
        normalized_vertices = bounding_poly[0]['normalizedVertices']
        xs = [vertice['x'] for vertice in normalized_vertices]
        ys = [vertice['y'] for vertice in normalized_vertices]
        x_min, y_min = min(xs), min(ys)
        x_max, y_max = max(xs), max(ys)
        x, y = (x_max + x_min) / 2, (y_max + y_min) / 2
        w, h = x_max - x_min, y_max - y_min

        converted_annotations.append((category, x, y, w, h))
    return converted_annotations


class YoloTransferLearning(TransferLearning):
    def train(self, assets_to_train):
        print(f'Launch training for {len(assets_to_train)} assets: {[asset["id"] for asset in assets_to_train]}')

        # Prepare folders for YOLO v3 framework
        folder = TemporaryDirectory()
        images_folder = os.path.join(folder.name, 'images')
        labels_folder = os.path.join(folder.name, 'labels')
        os.mkdir(images_folder)
        os.mkdir(labels_folder)
        full_image_names = []

        for asset in assets_to_train:
            filename = str(random.getrandbits(128))
            full_image_name = os.path.join(images_folder, f'{filename}.jpg')
            full_image_names.append(full_image_name)
            with open(full_image_name, 'wb') as f:
                content = asset['content']
                print(f'Downloading {content}...')
                response = requests.get(content, stream=True)
                if not response.ok:
                    continue
                for block in response.iter_content(1024):
                    if not block:
                        break
                    f.write(block)
            # TODO: Random train/test split
            annotations = convert_from_kili_to_yolo_format(asset['labels'][0])
            with open(os.path.join(labels_folder, f'{filename}.txt'), 'wb') as f:
                for category, x, y, w, h in annotations:
                    f.write(f'{category} {x} {y} {w} {h}\n'.encode())

        with open(COCO_TRAIN_TEST_TXT_FILE, 'wb') as f:
            for full_image_name in full_image_names:
                f.write(f'{full_image_name}\n'.encode())

        # Train with YOLO v3 framework
        train_parameters = ['python3', 'train.py',
                            '--cfg', f'{CONFIG_FILE}',
                            '--data', f'{COCO_DATA_FILE}',
                            '--cache-images']
        if self.current_training_number > 0:
            train_parameters.append('--resume')
        else:
            train_parameters.extend(['--weights', f'{WEIGHTS_FILE}'])
            train_parameters.extend(['--transfer'])
        print(f'Running training with parameters: {" ".join(train_parameters)}')
        subprocess.run(train_parameters)

    def predict(self, assets_to_predict):
        print(f'Launch inference for {len(assets_to_predict)} assets: {[asset["id"] for asset in assets_to_predict]}')

        # Format to YOLO
        input = TemporaryDirectory()
        output = TemporaryDirectory()
        filename_to_ids = {}
        for asset in assets_to_predict:
            filename = str(random.getrandbits(128))
            content = asset['content']
            image_name = f'{filename}.jpg'
            with open(os.path.join(input.name, image_name), 'wb') as f:
                response = requests.get(content, stream=True)
                if not response.ok:
                    continue
                for block in response.iter_content(1024):
                    if not block:
                        break
                    f.write(block)
            filename_to_ids[image_name] = asset['id']

        # Predict with YOLO v3 framework
        predict_parameters = ['python3', 'detect.py',
                              '--source', f'{input.name}',
                              '--output', f'{output.name}',
                              '--cfg', f'{CONFIG_FILE}',
                              '--weights', BEST_WEIGHTS_FILE]
        print(f'Running inference with parameters: {" ".join(predict_parameters)}')
        subprocess.run(predict_parameters)

        # Insert predictions to Kili Technology
        for filename in os.listdir(output.name):
            with open(os.path.join(output.name, filename), 'rb') as f:
                if filename.endswith('.txt'):
                    lines = f.readlines()
                    image_name = filename.replace('.txt', '')
                    image = Image.open(os.path.join(output.name, image_name))
                    total_width, total_height = image.size
                    annotations = []
                    for line in lines:
                        annotation = line.decode('utf-8')
                        [start, end, height, width, category, score, *_] = annotation.split(' ')
                        annotations.append(convert_from_yolo_to_kili_format(int(start), int(end), int(height),
                                                                            int(width), category, score, total_width,
                                                                            total_height))
                    asset_id = filename_to_ids[image_name]
                    print('Create predictions in Kili Technology...')
                    self.playground.create_prediction(asset_id=asset_id, json_response={'annotations': annotations})


def main():
    online_learning = YoloTransferLearning(EMAIL, PASSWORD, API_ENDPOINT, PROJECT_ID,
                                           minimum_number_of_assets_to_launch_training=3)

    print('Checking project configuration...')
    tools = online_learning.playground.get_tools(project_id=online_learning.project_id)
    assert len(tools) == 1
    json_settings = json.loads(tools[0]['jsonSettings'])
    assert 'annotation_types' in json_settings, 'Please configure project with Yolo classes as explained in README.md'
    categories = json_settings['annotation_types']
    for index, key in enumerate(categories):
        assert int(key) == index, 'Please follow Yolo format for labels'
    number_of_classes = len(categories)
    print('OK\n')

    print('Writing configuration...')
    with open(COCO_NAMES_FILE, 'wb') as f:
        for category in categories.values():
            f.write(f'{category}\n'.lower().encode())
    with open(COCO_DATA_FILE_TEMPLATE, 'rb') as f_template:
        with open(COCO_DATA_FILE, 'wb') as f:
            template = f_template.read().decode('utf-8') \
                .replace('%%NUMBER_OF_CLASSES%%', str(number_of_classes)) \
                .replace('%%COCO_TRAIN_TEST_TXT_FILE%%', COCO_TRAIN_TEST_TXT_FILE) \
                .replace('%%COCO_NAMES_FILE%%', COCO_NAMES_FILE)
            f.write(template.encode())
    with open(CONFIG_FILE_TEMPLATE, 'rb') as f_template:
        with open(CONFIG_FILE, 'wb') as f:
            number_of_filters = (4 + 1 + number_of_classes) * 3
            template = f_template.read().decode('utf-8') \
                .replace('%%NUMBER_OF_CLASSES%%', str(number_of_classes)) \
                .replace('%%NUMBER_OF_FILTERS%%', str(number_of_filters))
            f.write(template.encode())
    print('OK\n')

    print('Launching online learning...')
    online_learning.launch()
    print('OK\n')


if __name__ == '__main__':
    main()
