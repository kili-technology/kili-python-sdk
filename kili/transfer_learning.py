"""
Transfer Learning
"""

import subprocess
import time

from kili.client import Kili

SECONDS_TO_WAIT = 1
LABEL_FIELDS = ['isLatestLabelForUser', 'labelType', 'jsonResponse', 'createdAt']
FIELDS = ['id', 'content', 'externalId'] + [f'labels.{x}' for x in LABEL_FIELDS]


def get_labels_of_types(asset, label_types):
    """
    Extracts the latest labels from an asset

    Parameters
    ----------
    - asset: the asset to extract the labels from
    - label_types: type of label, either DEFAULT or REVIEW
    """
    labels = [label for label in asset['labels']
              if label['labelType'] in label_types and label['isLatestLabelForUser']]
    return sorted(labels, key=lambda label: label['createdAt'])


class TransferLearning:
    """
    TransferLearning
    """
    # pylint: disable=too-many-instance-attributes,too-many-arguments

    def __init__(
            self,
            api_key,
            api_endpoint,
            project_id,
            number_of_inferences,
            minimum_number_of_assets_to_launch_training=10):
        self.kili = Kili(api_key=api_key, api_endpoint=api_endpoint)
        self.api_key = api_key
        self.project_id = project_id
        self.current_inference_number = 0
        self.current_training_number = 0
        self.last_training_number = -1
        self.assets_seen_in_training = []
        self.minimum_number_of_assets_to_launch_training = \
            minimum_number_of_assets_to_launch_training
        self.number_of_inferences = number_of_inferences


    def get_assets_to_train(self):
        """
        Collects the assets to train on
        """
        assets = self.kili.assets(project_id=self.project_id, fields=FIELDS)
        assets_to_train = []
        for asset in assets:
            default_labels = get_labels_of_types(asset, ['DEFAULT'])
            review_labels = get_labels_of_types(asset, ['REVIEWED'])
            if len(review_labels) > 0:
                asset['labels'] = [review_labels[-1]]
                assets_to_train.append(asset)
            elif len(default_labels) == 1:
                asset['labels'] = [default_labels[-1]]
                assets_to_train.append(asset)
            elif len(review_labels) == 0 and len(default_labels) > 0:
                print(
                    f'Asset {asset["id"]} has several labels: it should be reviewed')
            else:
                continue
        return assets_to_train

    @staticmethod
    def train(assets_to_train):
        """
        Prints that training is ongoing
        """
        print(
            f'Launch training for {len(assets_to_train)} assets:' \
            f' {[asset["id"] for asset in assets_to_train]}')

    def launch_train(self):
        """
        Launches the training
        """
        print('Launching train')
        time.sleep(SECONDS_TO_WAIT)
        assets_to_train = self.get_assets_to_train()
        if len(self.assets_seen_in_training) == 0:
            filtered_assets_to_train = assets_to_train
        else:
            filtered_assets_to_train = [
                asset for asset in assets_to_train
                if all(asset['id'] not in training for training in self.assets_seen_in_training)]
        if len(filtered_assets_to_train) >= self.minimum_number_of_assets_to_launch_training:
            print('Starting training')
            TransferLearning.train(filtered_assets_to_train)
            self.current_training_number += 1
            self.assets_seen_in_training.append(
                [asset['id'] for asset in filtered_assets_to_train])
        else:
            print('Not enough labeled assets to start training')

    def get_assets_to_predict(self):
        """
        Collects the assets to predict
        """
        assets = self.kili.assets(project_id=self.project_id, fields=FIELDS)
        assets_to_predict = []
        for asset in assets:
            labels = get_labels_of_types(asset, ['DEFAULT', 'REVIEWED'])
            if len(labels) == 0:
                assets_to_predict.append(asset)
        return assets_to_predict

    @staticmethod
    def predict(assets_to_predict):
        """
        Prints that prediction is ongoing
        """
        print(
            f'Launch inference for {len(assets_to_predict)} assets:' \
            f' {[asset["id"] for asset in assets_to_predict]}')

    def launch_predict(self):
        """
        Launches the prediction
        """
        print('Launching prediction')
        time.sleep(SECONDS_TO_WAIT)
        if self.current_training_number == self.last_training_number:
            print('Inference will not be launched for now...')
            return
        assets_to_predict = self.get_assets_to_predict()
        if len(assets_to_predict) > 0:
            current_training_number = self.current_training_number
            TransferLearning.predict(assets_to_predict)
            self.last_training_number = current_training_number
            self.current_inference_number += 1

    @staticmethod
    def launch_tensorboard():
        """
        Launches the tensorboard
        """
        print('Starting Tensorboard...')
        with subprocess.Popen(['tensorboard', '--logdir=runs']) as proc:
            print(proc.stdout.read())

    def launch(self):
        """
        Launches the tensorboard, training and prediction
        """
        TransferLearning.launch_tensorboard()
        while self.current_inference_number < self.number_of_inferences:
            print(f'Iteration inference {self.current_inference_number}')
            self.launch_train()
            self.launch_predict()
