import argparse
import base64
import logging
import os
import random
import subprocess
from datetime import datetime
from tempfile import TemporaryDirectory
import random

import requests
from PIL import Image
from tqdm import tqdm

from kili.transfer_learning import TransferLearning

logging.basicConfig(
    format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)

random.seed(1337)

VALID_PERCENTAGE = 0.1
MAIN_PATH = os.path.dirname(os.path.realpath(__file__))
COCO_NAMES_FILE = 'data/custom_train.names'
COCO_TRAIN_TXT_FILE = 'data/custom_train.txt'
COCO_VALID_TXT_FILE = 'data/custom_valid.txt'
COCO_DATA_FILE = 'data/custom_train.data'
COCO_DATA_FILE_TEMPLATE = os.path.join(MAIN_PATH, 'coco.template.data')
CONFIG_FILE = 'cfg/yolov3-custom_train.cfg'
CONFIG_FILE_TEMPLATE = os.path.join(MAIN_PATH, 'yolov3.template.cfg')
BEST_WEIGHTS_FILE = 'weights/best.pt'
LAST_WEIGHTS_FILE = 'weights/last.pt'


def read_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--api_key", type=str,
                        default=os.environ.get('KILI_USER_API_KEY', None),
                        help="your api_key, for your kili credentials")
    parser.add_argument("-i", "--project_id", type=str,
                        default=os.environ.get('PROJECT_ID', None),
                        help="your kili project id")
    parser.add_argument("-j", "--job_id", type=str,
                        default=os.environ.get('JOB_ID', None),
                        help="job ID of the object detection task in Kili JSON settings")
    parser.add_argument("-a", "--api_endpoint", type=str,
                        default=os.environ.get('API_ENDPOINT', None),
                        help="the kili API endpoint you would like to use")
    parser.add_argument("-y", "--yolo_path", type=str,
                        default=os.environ.get('YOLO_PATH', None),
                        help="path to the yolov3 repository")
    parser.add_argument("-t", "--no_transfer", action="store_false",
                        help="if you want to apply transfer learning from pre-existing weights")
    parser.add_argument("-w", "--weights", type=str,
                        required=True,
                        help="path to weights you would like to use as initialization of for transfer learning")
    parser.add_argument("-o", "--override", action="store_true",
                        help="should we override the cfg file with your custom classes ?")
    parser.add_argument('-c', "--cfg", type=str,
                        help="cfg file you would like to use")
    parser.add_argument('-g', "--number_of_inferences", type=int,
                        help="maximal number of inferences")
    args = parser.parse_args()
    if any([
            not args.api_key,
            not args.project_id,
            not args.yolo_path]):
        logging.error("Some required arguments are empty")
        exit(parser.print_usage())
    else:
        return args


def convert_from_yolo_to_kili_format(x1, y1, x2, y2, category, score, total_width, total_height):
    time_hash = datetime.now().strftime('%Y%m%d%H%M%S')
    annotations = {
        'score': float(score),
        'mid': f'{time_hash}-{random.getrandbits(52)}',
        'categories': [{'name': str(category),
                        'confidence': int(float(score) * 100)}],
        'boundingPoly': [
            {'normalizedVertices': [
                {'x': x1 / total_width, 'y': y1 / total_height},
                {'x': x2 / total_width, 'y': y1 / total_height},
                {'x': x1 / total_width, 'y': y2 / total_height},
                {'x': x2 / total_width, 'y': y2 / total_height},
            ]}
        ],
        'type': 'rectangle'
    }

    return annotations


def convert_from_kili_to_yolo_format(job_id, label):
    if 'jsonResponse' not in label:
        return []
    json_response = label['jsonResponse']
    if 'annotations' not in json_response:
        return []
    annotations = json_response[job_id]['annotations']
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
    def __init__(self, api_key, api_endpoint, project_id, transfer, weights, override_cfg, cfg, job_id, number_of_inferences):
        TransferLearning.__init__(
            self, api_key, api_endpoint, project_id, number_of_inferences)
        self.transfer = transfer
        self.weights = weights
        self.override_cfg = override_cfg
        self.cfg = cfg
        self.job_id = job_id

    def train(self, assets_to_train):
        logging.info(f'Launch training for {len(assets_to_train)} assets.')

        # Prepare folders for YOLO v3 framework
        folder = TemporaryDirectory()
        images_folder = os.path.join(folder.name, 'train', 'images')
        labels_folder = os.path.join(folder.name, 'train', 'labels')
        images_valid_folder = os.path.join(folder.name, 'valid', 'images')
        labels_valid_folder = os.path.join(folder.name, 'valid', 'labels')
        for folder in [images_folder, labels_folder, images_valid_folder, labels_valid_folder]:
            os.makedirs(folder)

        train_full_image_names = []
        valid_full_image_names = []

        logging.info("Downloading assets...")
        for asset in tqdm(assets_to_train):
            is_valid = random.random() < VALID_PERCENTAGE
            image_destination_folder = images_valid_folder if is_valid else images_folder
            labels_destination_folder = labels_valid_folder if is_valid else labels_folder
            filename = str(random.getrandbits(128))
            full_image_name = os.path.join(
                image_destination_folder, f'{filename}.jpg')
            if is_valid:
                valid_full_image_names.append(full_image_name)
            else:
                train_full_image_names.append(full_image_name)

            with open(full_image_name, 'wb') as f:
                content = asset['content']
                response = requests.get(content, stream=True)
                if not response.ok:
                    logging.warn('Error while downloading image %s' %
                                 asset['id'])
                    continue
                for block in response.iter_content(1024):
                    if not block:
                        break
                    f.write(block)

            annotations = convert_from_kili_to_yolo_format(
                self.job_id, asset['labels'][0])
            with open(os.path.join(labels_destination_folder, f'{filename}.txt'), 'wb') as f:
                for category, x, y, w, h in annotations:
                    f.write(f'{category} {x} {y} {w} {h}\n'.encode())

        with open(COCO_TRAIN_TXT_FILE, 'wb') as f:
            for full_image_name in train_full_image_names:
                f.write(f'{full_image_name}\n'.encode())

        with open(COCO_VALID_TXT_FILE, 'wb') as f:
            for full_image_name in valid_full_image_names:
                f.write(f'{full_image_name}\n'.encode())

        logging.info("Image download done.")
        logging.info("Train images : " + str(len(train_full_image_names)))
        logging.info("Valid images : " + str(len(valid_full_image_names)))

        # Train with YOLO v3 framework
        train_parameters = ['python3', 'train.py',
                            '--data', f'{COCO_DATA_FILE}',
                            '--cache-images']
        if not self.override_cfg:
            train_parameters.extend(['--cfg', f'{CONFIG_FILE}'])
        else:
            train_parameters.extend(['--cfg', self.cfg])
        if self.current_training_number > 0:
            logging.info('Resuming training...')
            train_parameters.append('--resume')
        else:
            logging.info('Launching new training...')
            train_parameters.extend(['--weights', self.weights])
            if self.transfer:
                train_parameters.append('--transfer')
        logging.info(
            f'Running training with parameters: {" ".join(train_parameters)}')
        subprocess.run(train_parameters)

    def predict(self, assets_to_predict):
        logging.info(
            f'Launch inference for {len(assets_to_predict)} assets: {[asset["id"] for asset in assets_to_predict]}')

        # Format to YOLO
        input = TemporaryDirectory()
        output = TemporaryDirectory()
        filename_to_ids = {}
        for asset in assets_to_predict:
            filename = str(random.getrandbits(128))
            content = asset['content']
            image_name = f'{filename}.jpg'
            filename_to_ids[image_name] = asset['externalId']
            if not content.startswith('http://') and not content.startswith('https://'):
                with open(os.path.join(input.name, image_name), 'wb') as f:
                    content = content.replace('data:image/jpeg;base64,', '')
                    f.write(base64.b64decode(content))
                continue
            with open(os.path.join(input.name, image_name), 'wb') as f:
                response = requests.get(content, stream=True)
                if not response.ok:
                    continue
                for block in response.iter_content(1024):
                    if not block:
                        break
                    f.write(block)

        # Predict with YOLO v3 framework
        weights = BEST_WEIGHTS_FILE if os.path.isfile(
            BEST_WEIGHTS_FILE) else self.weights
        predict_parameters = ['python3', 'detect.py',
                              '--save-txt',
                              '--source', f'{input.name}',
                              '--output', f'{output.name}',
                              '--cfg', f'{CONFIG_FILE}',
                              '--weights', weights]
        logging.info(
            f'Running inference with parameters: {" ".join(predict_parameters)}')
        subprocess.run(predict_parameters)

        # Insert predictions to Kili Technology
        external_id_array = []
        json_response_array = []
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
                        [start, end, height, width, category,
                            score, *_] = annotation.split(' ')
                        annotations.append(convert_from_yolo_to_kili_format(int(start), int(end), int(height),
                                                                            int(
                                                                                width), category, score, total_width,
                                                                            total_height))
                    external_id_array.append(filename_to_ids[image_name])
                    json_response_array.append(
                        {self.job_id: {'annotations': annotations}})
        logging.info('Create predictions in Kili Technology...')
        model_name = datetime.now().strftime('model-yolo-%Y%m%d-%H%M%S')
        self.kili.create_predictions(project_id=self.project_id,
                                           external_id_array=external_id_array,
                                           model_name_array=[
                                               model_name] * len(external_id_array),
                                           json_response_array=json_response_array)


def main():
    args = read_arguments()
    os.chdir(args.yolo_path)

    transfer_learning = YoloTransferLearning(
        api_key=args.api_key, api_endpoint=args.api_endpoint, project_id=args.project_id,
        transfer=args.no_transfer, weights=args.weights, override_cfg=args.override, cfg=args.cfg, job_id=args.job_id,
        number_of_inferences=args.number_of_inferences
    )

    logging.info('Checking project configuration...')
    project = transfer_learning.kili.projects(
        project_id=transfer_learning.project_id)[0]
    try:
        categories = project['jsonInterface']['jobs'][transfer_learning.job_id]['content']['categories']
    except KeyError:
        raise Exception(
            'Please configure project with Yolo classes as explained in README.md')
    for index, key in enumerate(categories):
        assert int(key) == index, 'Please follow Yolo format for labels'
        assert 'name' in categories[key]
    number_of_classes = len(categories)
    logging.info('OK\n')

    logging.info('Writing configuration...')
    with open(COCO_NAMES_FILE, 'wb') as f:
        for category in categories.values():
            category_name = category['name']
            f.write(f'{category_name}\n'.lower().encode())
    with open(COCO_DATA_FILE_TEMPLATE, 'rb') as f_template:
        with open(COCO_DATA_FILE, 'wb') as f:
            template = f_template.read().decode('utf-8') \
                .replace('%%NUMBER_OF_CLASSES%%', str(number_of_classes)) \
                .replace('%%COCO_TRAIN_TXT_FILE%%', COCO_TRAIN_TXT_FILE) \
                .replace('%%COCO_VALID_TXT_FILE%%', COCO_VALID_TXT_FILE) \
                .replace('%%COCO_NAMES_FILE%%', COCO_NAMES_FILE)
            f.write(template.encode())
    if not args.override:
        with open(CONFIG_FILE_TEMPLATE, 'rb') as f_template:
            with open(CONFIG_FILE, 'wb') as f:
                number_of_filters = (4 + 1 + number_of_classes) * 3
                template = f_template.read().decode('utf-8') \
                    .replace('%%NUMBER_OF_CLASSES%%', str(number_of_classes)) \
                    .replace('%%NUMBER_OF_FILTERS%%', str(number_of_filters))
                f.write(template.encode())
    logging.info('OK\n')

    logging.info('Launching transfer learning...')
    transfer_learning.launch()
    logging.info('OK\n')


if __name__ == '__main__':
    main()
