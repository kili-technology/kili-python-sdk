import os
import time
from tempfile import TemporaryDirectory

import requests
from PIL import Image
from models import *
from utils.datasets import *
from utils.utils import *

from kili.authentication import KiliAuth
from kili.playground import Playground

EMAIL = os.environ['EMAIL']
PASSWORD = os.environ['PASSWORD']
PROJECT_ID = os.environ['PROJECT_ID']
API_ENDPOINT = os.environ['API_ENDPOINT']

SECONDS_BETWEEN_TRAININGS = 10
CONFIG = 'data/yolov3-spp.cfg'
DATA = 'data/coco.data'
WEIGHTS = 'data/yolov3-spp.weights'
CONFIDENCE_THRESHOLD = 0.3
NON_MAX_SUPPRESSION_THRESHOLD = 0.5
IMAGE_SIZE = (320, 192)


def detect(source, output):
    # Initialize
    device = torch_utils.select_device(device='cpu')
    model = Darknet(CONFIG, IMAGE_SIZE)

    # Load weights
    attempt_download(WEIGHTS)
    if WEIGHTS.endswith('.pt'):
        model.load_state_dict(torch.load(WEIGHTS, map_location=device)['model'])
    else:
        _ = load_darknet_weights(model, WEIGHTS)

    model.to(device).eval()

    dataset = LoadImages(source, img_size=IMAGE_SIZE, half=False)

    classes = load_classes(parse_data_cfg(DATA)['names'])

    result = []

    # Run inference
    t0 = time.time()
    for path, img, im0s, vid_cap in dataset:
        t = time.time()

        # Get detections
        img = torch.from_numpy(img).to(device)
        if img.ndimension() == 3:
            img = img.unsqueeze(0)
        predictions = model(img)[0]

        # Apply NMS
        predictions = non_max_suppression(predictions, CONFIDENCE_THRESHOLD, NON_MAX_SUPPRESSION_THRESHOLD)

        for i, prediction in enumerate(predictions):
            p, s, im0 = path, '', im0s

            save_path = str(Path(output) / Path(p).name)
            s += '%gx%g ' % img.shape[2:]
            if prediction is not None and len(prediction):
                # Rescale boxes from img_size to im0 size
                prediction[:, :4] = scale_coords(img.shape[2:], prediction[:, :4], im0.shape).round()

                # Print results
                for c in prediction[:, -1].unique():
                    n = (prediction[:, -1] == c).sum()
                    s += '%g %ss, ' % (n, classes[int(c)])

                # Write results
                for *xyxy, conf, _, cls in prediction:
                    with open(save_path + '.txt', 'a') as file:
                        file.write(('%g ' * 6 + '\n') % (*xyxy, cls, conf))
                        result.append([*xyxy, cls, conf])

            print('%sDone. (%.3fs)' % (s, time.time() - t))
            cv2.imwrite(save_path, im0)

    print('Done. (%.3fs)' % (time.time() - t0))
    return result


def extract_train_for_autoML(assets):
    X = []
    y = []
    X_to_be_predicted = []
    ids_X_to_be_predicted = []
    for asset in assets:
        x = asset['content']
        labels = [l for l in asset['labels']
                  if l['labelType'] in ['DEFAULT', 'REVIEWED']]

        if len(labels) == 0:
            X_to_be_predicted.append(x)
            ids_X_to_be_predicted.append(asset['id'])

    return X, y, X_to_be_predicted, ids_X_to_be_predicted


def convert_from_yolo_to_google_format(x1, y1, x2, y2, category, score, total_width, total_height):
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


def main():
    kauth = KiliAuth(EMAIL, PASSWORD, api_endpoint=API_ENDPOINT)
    playground = Playground(kauth)

    while True:
        time.sleep(SECONDS_BETWEEN_TRAININGS)
        tools = playground.get_tools(project_id=PROJECT_ID)
        assert len(tools) == 1
        tool = tools[0]
        assert tool['toolType'] == 'IMAGE'
        with open('data/coco.names', 'rb') as f:
            json_settings = {"tools": ["rectangle"], "annotation_types": {}}
            lines = f.readlines()
            for index, line in enumerate(lines):
                category = line.decode('utf-8').strip()
                if category:
                    json_settings['annotation_types'][str(index)] = category
        print('Configure project to use Coco\'s classes...')
        playground.update_tool(tool_id=tool['id'], project_id=PROJECT_ID, name='', tool_type='IMAGE',
                               json_settings=json_settings)

        print('Export assets and labels...')
        assets = playground.export_assets(project_id=PROJECT_ID)
        print('Extract assets to predict...')
        if assets is None:
            continue
        X, y, X_to_be_predicted, ids_X_to_be_predicted = extract_train_for_autoML(assets)

        folder = TemporaryDirectory()
        output = TemporaryDirectory()
        for X, _id in zip(X_to_be_predicted, ids_X_to_be_predicted):
            if '.' in X.split('/')[-1]:
                extension = X.split('.')[-1]
            else:
                extension = '.jpg'
            with open(os.path.join(folder.name, f'{_id}.{extension}'), 'wb') as f:
                response = requests.get(X, stream=True)
                if not response.ok:
                    continue
                for block in response.iter_content(1024):
                    if not block:
                        break
                    f.write(block)

        print('Predicting...')
        detect(folder.name, output.name)
        for d in os.listdir(output.name):
            with open(os.path.join(output.name, d), 'rb') as f:
                if d.endswith('.txt'):
                    lines = f.readlines()
                    image_name = d.replace('.txt', '')
                    image = Image.open(os.path.join(output.name, image_name))
                    total_width, total_height = image.size
                    annotations = []
                    for line in lines:
                        annotation = line.decode('utf-8')
                        [start, end, height, width, category, score, *_] = annotation.split(' ')
                        annotations.append(convert_from_yolo_to_google_format(int(start), int(end), int(height),
                                                                              int(width), category, score, total_width,
                                                                              total_height))
                    _id = d.split('.')[0]
                    print('Create predictions in Kili Technology...')
                    playground.create_prediction(asset_id=_id, json_response={'annotations': annotations})
        print('Done.\n')


if __name__ == '__main__':
    main()
