import argparse
import logging
import os
import yaml
import json

from kili.client import Kili

logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)


def read_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--api_key", type=str,
                        default=os.environ.get('EMAIL', None),
                        help="your email, part of your kili credentials")
    parser.add_argument("-i", "--project_id", type=str,
                        default=os.environ.get('PROJECT_ID', None),
                        help="your kili project id")
    parser.add_argument("-a", "--api_endpoint", type=str,
                        default=os.environ.get('API_ENDPOINT', None),
                        help="the kili API endpoint you would like to use")
    parser.add_argument("-a", "--annotations_path", type=str,
                        required=True,
                        help="the path to your prediction yml file")
    args = parser.parse_args()
    if any([
        not args.api_key, 
        not args.project_id]):
        logging.error("Some required arguments are empty")
        exit(parser.print_usage())
    else:
        return args

def main():
    logging.info("Reading & parsing arguments...")
    args = read_arguments()

    logging.info("Reading predictions files")
    with open(args.annotations_path, 'r') as f:
        configuration = yaml.safe_load(f)

    predictions = configuration['predictions']

    logging.info("Connecting to Kili")
    kili = Kili(api_key=args.api_key, api_endpoint=args.api_endpoint)

    logging.info("Getting predictions")
    external_id_array = [
        get(prediction, 'externalId') for prediction in predictions
    ]
    json_response_array = [
        json.loads(get(prediction, 'response')) for prediction in predictions
    ]

    logging.info("Uploading to Kili")
    kili.create_predictions(
        project_id=args.project_id,
        external_id_array=external_id_array, json_response_array=json_response_array
    )

if __name__ == '__main__':
    main()
