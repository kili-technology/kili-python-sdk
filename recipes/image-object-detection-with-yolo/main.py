import argparse
import json
import logging
import os
import random
import subprocess
from tempfile import TemporaryDirectory
import requests
from tqdm import tqdm

from PIL import Image

from kili.transfer_learning import TransferLearning

logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)

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
    parser.add_argument("-e", "--email", type=str,
                        default=os.environ.get('EMAIL', None),
                        help="your email, part of your kili credentials")
    parser.add_argument("-p", "--password", type=str,
                        default=os.environ.get('PASSWORD', None),
                        help="your password, part of your kili credentials")
    parser.add_argument("-i", "--project_id", type=str,
                        default=os.environ.get('PROJECT_ID', None),
                        help="your kili project id")
    parser.add_argument("-a", "--api_endpoint", type=str,
                        default=os.environ.get('API_ENDPOINT', None),
                        help="the kili API endpoint you would like to use")
    parser.add_argument("-y", "--yolo_path", type=str,
                        default=os.environ.get('YOLO_PATH', None),
                        help="path to the yolov3 repository")
    parser.add_argument("-t", "--no_transfer", action="store_false",
                        help="if you want to apply transfer learning from pre-existing weights")
    parser.add_argument("-w", "--weights", type=str, 
                        required=True, help="path to weights you would like to use as initialization of for transfer learning")
    parser.add_argument("-o", "--override", action="store_true", 
                        help="should we override the cfg file with your custom classes ?")
    parser.add_argument('-c', "--cfg", type=str,
                        help="cfg file you would like to use")
    args = parser.parse_args()
    if any([
        not args.email, 
        not args.password, 
        not args.project_id, 
        not args.yolo_path]):
        logging.error("Some required arguments are empty")
        exit(parser.print_usage())
    else:
        return args


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
    def __init__(self, email, password, api_endpoint, project_id, transfer, weights, override_cfg, cfg):
        TransferLearning.__init__(self, email, password, api_endpoint, project_id)
        self.transfer = transfer
        self.weights = weights
        self.override_cfg = override_cfg
        self.cfg = cfg

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
            full_image_name = os.path.join(image_destination_folder, f'{filename}.jpg')
            if is_valid:
                valid_full_image_names.append(full_image_name)
            else:
                train_full_image_names.append(full_image_name)

            with open(full_image_name, 'wb') as f:
                content = asset['content']
                response = requests.get(content, stream=True)
                if not response.ok:
                    logging.warn('Error while downloading image %s' % asset['id'])
                    continue
                for block in response.iter_content(1024):
                    if not block:
                        break
                    f.write(block)

            annotations = convert_from_kili_to_yolo_format(asset['labels'][0])
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
        logging.info(f'Running training with parameters: {" ".join(train_parameters)}')
        subprocess.run(train_parameters)
        

    def predict(self, assets_to_predict):
        logging.info(f'Launch inference for {len(assets_to_predict)} assets: {[asset["id"] for asset in assets_to_predict]}')

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
        logging.info(f'Running inference with parameters: {" ".join(predict_parameters)}')
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
                    logging.info('Create predictions in Kili Technology...')
                    self.playground.create_prediction(asset_id=asset_id, json_response={'annotations': annotations})


def main():
    args = read_arguments()
    os.chdir(args.yolo_path)

    transfer_learning = YoloTransferLearning(
        args.email, args.password, args.api_endpoint, args.project_id,
        transfer=args.no_transfer, weights=args.weights, override_cfg=args.override, cfg=args.cfg
    )

    logging.info('Checking project configuration...')
    tools = transfer_learning.playground.get_tools(project_id=transfer_learning.project_id)
    assert len(tools) == 1
    json_settings = json.loads(tools[0]['jsonSettings'])
    assert 'annotation_types' in json_settings, 'Please configure project with Yolo classes as explained in README.md'
    categories = json_settings['annotation_types']
    for index, key in enumerate(categories):
        assert int(key) == index, 'Please follow Yolo format for labels'
    number_of_classes = len(categories)
    logging.info('OK\n')

    logging.info('Writing configuration...')
    with open(COCO_NAMES_FILE, 'wb') as f:
        for category in categories.values():
            f.write(f'{category}\n'.lower().encode())
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
