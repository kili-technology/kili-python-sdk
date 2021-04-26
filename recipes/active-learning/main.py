import argparse
import random
import os
import logging
from tqdm import tqdm

from kili.client import Kili

logging.basicConfig(
    format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)


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
    args = parser.parse_args()
    if any([
            not args.email,
            not args.password,
            not args.project_id]):
        logging.error("Some required arguments are empty")
        exit(parser.print_usage())
    else:
        return args


class ActiveLearner:
    def __init__(self, email, password, api_endpoint, project_id):
        self.kili = Kili(email, password, api_endpoint=api_endpoint)
        self.project_id = project_id

    def get_assets_to_evaluate(self):
        assets = self.kili.assets(project_id=self.project_id)
        assets_to_evaluate = []
        for asset in assets:
            if len(asset['labels']) == 0:
                assets_to_evaluate.append(asset)

        return assets_to_evaluate

    def prioritize_assets(self, assets, scorer, *args, **kwargs):
        assets_score = [scorer(asset, *args, **kwargs) for asset in assets]
        ranked_assets_with_score = sorted(
            list(zip(assets, assets_score)), key=lambda x: x[1], reverse=True)
        ranked_assets = [asset_with_score[0]
                         for asset_with_score in ranked_assets_with_score]
        return ranked_assets

    def update_assets_priority(self, assets):
        for i, asset in enumerate(tqdm(assets)):
            asset_id = asset['id']
            self.kili.update_properties_in_assets(
                asset_id=[asset_id], priorities=[i])
        return True


def scorer(asset, *args, **kwargs):
    return random.random()


def main():
    logging.info("Reading & parsing arguments...")
    args = read_arguments()

    logging.info("Connecting to Kili...")
    active_learner = ActiveLearner(
        args.email,
        args.password,
        args.api_endpoint,
        args.project_id
    )

    logging.info("Getting unlabeled assets...")
    to_evaluate_assets = active_learner.get_assets_to_evaluate()

    logging.info("Ranking assets...")
    ranked_assets = active_learner.prioritize_assets(
        to_evaluate_assets, scorer)

    logging.info("Sending back assets in priority order to Kili...")
    active_learner.update_assets_priority(ranked_assets)

    logging.info("Done !")


if __name__ == '__main__':
    main()
