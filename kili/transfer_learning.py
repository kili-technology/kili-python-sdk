import subprocess
import time

from kili.authentication import KiliAuth
from kili.playground import Playground

SECONDS_TO_WAIT = 10


def get_labels_of_types(asset, label_types):
    labels = [label for label in asset['labels']
              if label['labelType'] in label_types and label['isLatestLabelForUser']]
    return sorted(labels, key=lambda label: label['createdAt'])


class TransferLearning:
    def __init__(self, email, password, api_endpoint, project_id, number_of_inferences, minimum_number_of_assets_to_launch_training=100):
        kauth = KiliAuth(email, password, api_endpoint=api_endpoint)

        self.playground = Playground(kauth)
        self.project_id = project_id
        self.current_inference_number = 0
        self.current_training_number = 0
        self.last_training_number = -1
        self.assets_seen_in_training = []
        self.minimum_number_of_assets_to_launch_training = minimum_number_of_assets_to_launch_training
        self.number_of_inferences = number_of_inferences

    def _current_training_number(self):
        return self.current_training_number

    def get_assets_to_train(self):
        assets = self.playground.assets(project_id=self.project_id)
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

    def train(self, assets_to_train):
        print(
            f'Launch training for {len(assets_to_train)} assets: {[asset["id"] for asset in assets_to_train]}')
        return

    def launch_train(self):
        time.sleep(SECONDS_TO_WAIT)
        assets_to_train = self.get_assets_to_train()
        if len(self.assets_seen_in_training) == 0:
            filtered_assets_to_train = assets_to_train
        else:
            filtered_assets_to_train = [asset for asset in assets_to_train
                                        if all([asset['id'] not in training
                                                for training in self.assets_seen_in_training])]
        if len(filtered_assets_to_train) >= self.minimum_number_of_assets_to_launch_training:
            self.train(filtered_assets_to_train)
            self.current_training_number += 1
            self.assets_seen_in_training.append(
                [asset['id'] for asset in filtered_assets_to_train])

    def get_assets_to_predict(self):
        assets = self.playground.assets(project_id=self.project_id)
        assets_to_predict = []
        for asset in assets:
            labels = get_labels_of_types(asset, ['DEFAULT', 'REVIEWED'])

            if len(labels) == 0:
                assets_to_predict.append(asset)

        return assets_to_predict

    def predict(self, assets_to_predict):
        print(
            f'Launch inference for {len(assets_to_predict)} assets: {[asset["id"] for asset in assets_to_predict]}')
        return

    def launch_predict(self):
        time.sleep(SECONDS_TO_WAIT)
        if self.current_training_number == self.last_training_number:
            print('Inference will not be launched for now...')
            return
        assets_to_predict = self.get_assets_to_predict()
        if len(assets_to_predict) > 0:
            current_training_number = self.current_training_number
            self.predict(assets_to_predict)
            self.last_training_number = current_training_number
            self.current_inference_number += 1

    def launch_tensorboard(self):
        print('Starting Tensorboard...')
        subprocess.Popen(['tensorboard', '--logdir=runs'])
        print('You can access Tensorboard at http://localhost:6006\n')

    def launch(self):
        self.launch_tensorboard()
        while self.current_inference_number < self.number_of_inferences:
            self.launch_train()
            self.launch_predict()
