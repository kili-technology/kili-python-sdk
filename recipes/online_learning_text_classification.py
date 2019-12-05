import os
import getpass
from tqdm import tqdm
import click
import json
import warnings
import time
from tempfile import TemporaryDirectory
from dotenv import load_dotenv
import os

import numpy as np
import autosklearn
import autosklearn.classification
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_classif
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from kili.authentication import KiliAuth
from kili.playground import Playground


warnings.filterwarnings('ignore', 'Mean of empty slice')

NGRAM_RANGE = (1, 2)
TOP_K = 20000
TOKEN_MODE = 'word'
MIN_DOC_FREQ = 2
SECONDS_BETWEEN_TRAININGS = 0


def ngram_vectorize(train_texts, train_labels, val_texts):
    kwargs = {
        'ngram_range': NGRAM_RANGE,
        'dtype': 'int32',
        'strip_accents': 'unicode',
        'decode_error': 'replace',
        'analyzer': TOKEN_MODE,
        'min_df': MIN_DOC_FREQ,
    }

    # Learn Vocab from train texts and vectorize train and val sets
    tfidf_vectorizer = TfidfVectorizer(**kwargs)
    x_train = tfidf_vectorizer.fit_transform(train_texts)
    x_val = tfidf_vectorizer.transform(val_texts)

    # Select best k features, with feature importance measured by f_classif
    selector = SelectKBest(f_classif, k=min(TOP_K, x_train.shape[1]))
    selector.fit(x_train, train_labels)
    x_train = selector.transform(x_train).astype('float32')
    x_val = selector.transform(x_val).astype('float32')
    return x_train, x_val


def extract_train_for_autoML(assets, categories, train_test_threshold=0.8):
    X = []
    y = []
    X_to_be_predicted = []
    ids_X_to_be_predicted = []
    for asset in assets:
        x = asset['content']
        labels = [l for l in asset['labels']
                  if l['labelType'] in ['DEFAULT', 'REVIEWED']]

        # If not label, adds it to X_to_be_predicted
        if len(labels) == 0:
            X_to_be_predicted.append(x)
            ids_X_to_be_predicted.append(asset['id'])

        # Otherwise adds it to training examples X, y
        for label in labels:
            jsonResponse = json.loads(label['jsonResponse'])
            is_empty_label = 'categories' not in jsonResponse or len(
                jsonResponse['categories']) != 1 or 'name' not in jsonResponse['categories'][0]
            if is_empty_label:
                continue
            X.append(x)
            y.append(categories.index(
                jsonResponse['categories'][0]['name']))
    return X, y, X_to_be_predicted, ids_X_to_be_predicted


def automl_train_and_predict(X, y, X_to_be_predicted):
    x, x_to_be_predicted = ngram_vectorize(
        X, y, X_to_be_predicted)
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42)

    tmp_folder = TemporaryDirectory()
    output_folder = TemporaryDirectory()

    cls = autosklearn.classification.AutoSklearnClassifier(n_jobs=4, time_left_for_this_task=200,
                                                           per_run_time_limit=20,
                                                           tmp_folder=tmp_folder.name,
                                                           output_folder=output_folder.name,
                                                           seed=10)
    cls.fit(x_train, y_train)
    assert x_train.shape[1] == x_to_be_predicted.shape[1]

    # Performance metric
    predictions_test = cls.predict(x_test)
    print('Accuracy: {}'.format(accuracy_score(y_test, predictions_test)))

    #
    predictions = cls.predict(x_to_be_predicted)
    return predictions


@click.command()
@click.option('--api_endpoint', default='https://cloud.kili-technology.com/api/label/graphql', help='Endpoint of GraphQL client')
def main(api_endpoint):

    if os.path.exists('.env'):
        load_dotenv()
        email = os.getenv('EMAIL')
        password = os.getenv('PASSWORD')
        project_id = os.getenv('PROJECT_ID')
        api_endpoint = os.getenv('API_ENDPOINT')
    else:
        email = input('Enter Email: ')
        password = getpass.getpass('Enter password for user {}:'.format(email))
        project_id = input('Enter project id: ')

    kauth = KiliAuth(email, password, api_endpoint=api_endpoint)
    playground = Playground(kauth)

    # Check and load new predictions
    STOP_CONDITION = True
    while STOP_CONDITION:
        tools = playground.get_tools(project_id=project_id)
        assert len(tools) == 1
        categories = list(json.loads(tools[0]['jsonSettings'])[
                          'categories'].keys())

        print('Export assets and labels...')
        assets = playground.export_assets(project_id=project_id)
        print('Done.\n')
        X, y, X_to_be_predicted, ids_X_to_be_predicted = extract_train_for_autoML(
            assets, categories)

        if len(X) > 5:
            print('Online Learning is on its way...')
            predictions = automl_train_and_predict(X, y, X_to_be_predicted)
            # Insert pre-annotations
            for i, prediction in enumerate(tqdm(predictions)):
                json_response = {'categories': [
                    {'name': categories[prediction], 'confidence':100}]}
                id = ids_X_to_be_predicted[i]
                playground.create_prediction(
                    asset_id=id, json_response=json_response)
            print('Done.\n')
        time.sleep(SECONDS_BETWEEN_TRAININGS)


if __name__ == '__main__':
    main()
