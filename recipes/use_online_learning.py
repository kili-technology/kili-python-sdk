import os
import getpass
import tarfile
import urllib.request
from tqdm import tqdm
import click
import json
import shutil


import numpy as np
import matplotlib.pyplot as plt

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_classif
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_recall_fscore_support

import autosklearn
import autosklearn.classification

from kili.authentication import authenticate
from kili.mutations.asset import append_to_dataset
from kili.mutations.label import create_prediction, append_to_labels
from kili.queries.asset import get_assets_by_external_id, export_assets


NGRAM_RANGE = (1, 2)
TOP_K = 20000
TOKEN_MODE = 'word'
MIN_DOC_FREQ = 2
converter_label_to_name = {0: "NEGATIVE", 1: "POSITIVE"}
converter_name_to_label = {"NEGATIVE": 0, "POSITIVE": 1}

def download_dataset():
    url = 'https://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz'
    filename = url.split('/')[-1]
    target_path = os.path.join('/tmp', filename)
    if not os.path.exists(target_path):
        print('downloading...')
        urllib.request.urlretrieve(url, target_path)
    return target_path

def extract_dataset(path):
    target_path = './IMDB'
    if not os.path.exists(target_path):
        tar = tarfile.open(path)
        tar.extractall(path=target_path)
        tar.close()
    return target_path

def shuffle(X, y):
    perm = np.random.RandomState(seed=10).permutation(len(X))
    X = X[perm]
    y = y[perm]
    return X, y

def load_imdb_dataset(path):
    imdb_path = os.path.join(path)

    # Load the dataset
    train_texts = []
    train_labels = []
    test_texts = []
    test_labels = []
    for dset in ['train', 'test']:
        for cat in ['pos', 'neg']:
            dset_path = os.path.join(imdb_path, dset, cat)
            for fname in sorted(os.listdir(dset_path)):
                if fname.endswith('.txt'):
                    with open(os.path.join(dset_path, fname)) as f:
                        if dset == 'train': train_texts.append(f.read())
                        else: test_texts.append(f.read())
                    label = 0 if cat == 'neg' else 1
                    if dset == 'train': train_labels.append(label)
                    else: test_labels.append(label)

    # Converting to np.array
    train_texts = np.array(train_texts)
    train_labels = np.array(train_labels)
    test_texts = np.array(test_texts)
    test_labels = np.array(test_labels)

    # Shuffle the training dataset
    train_texts, train_labels = shuffle(train_texts, train_labels)
    test_texts, test_labels = shuffle(test_texts, test_labels)


    # Return the dataset
    return train_texts, train_labels, test_texts, test_labels

def plot_sample_length_distribution(figure_path, X_train):
    plt.figure(figsize=(15, 10))
    plt.hist([len(sample) for sample in list(X_train)], 50)
    plt.xlabel('Length of samples')
    plt.ylabel('Number of samples')
    plt.title('Sample length distribution')
    plt.savefig(os.path.join(figure_path, "length_distribution.png"), dpi=200)

def plot_most_frequent_words_or_ngrams(figure_path, X_train, ngram_range = (1,1)):
    kwargs = {
        'ngram_range' : ngram_range,
        'dtype' : 'int32',
        'strip_accents' : 'unicode',
        'decode_error' : 'replace',
        'analyzer' : TOKEN_MODE,
    }
    vectorizer = CountVectorizer(**kwargs)
    vect_texts = vectorizer.fit_transform(list(X_train))
    all_ngrams = vectorizer.get_feature_names()
    num_ngrams = min(50, len(all_ngrams))
    all_counts = vect_texts.sum(axis=0).tolist()[0]

    all_ngrams, all_counts = zip(*[(n, c) for c, n in sorted(zip(all_counts, all_ngrams), reverse=True)])
    ngrams = all_ngrams[:num_ngrams]
    counts = all_counts[:num_ngrams]

    idx = np.arange(num_ngrams)

    plt.figure(figsize=(30, 30))
    plt.bar(idx, counts, width=0.8)
    plt.xlabel('N-grams')
    plt.ylabel('Frequencies')
    plt.title('Frequency distribution of ngrams')
    plt.xticks(idx, ngrams, rotation=45)
    plt.savefig(os.path.join(figure_path, "most_frequent_ngrams.png"), dpi=200)

def ngram_vectorize(train_texts, train_labels, val_texts):
    kwargs = {
        'ngram_range' : NGRAM_RANGE,
        'dtype' : 'int32',
        'strip_accents' : 'unicode',
        'decode_error' : 'replace',
        'analyzer' : TOKEN_MODE,
        'min_df' : MIN_DOC_FREQ,
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

def print_infos_dataset(X_train,y_train,X_test,y_test):
    print ('Train samples shape: {} | train labels shape: {}'.format(X_train.shape, y_train.shape))
    print ('Test samples shape: {} | test labels shape: {}'.format(X_test.shape, y_test.shape))
    
    uniq_class_arr, counts = np.unique(y_train, return_counts=True)
    print ('Number of unique classes : {}'.format(len(uniq_class_arr)))
    for _class in uniq_class_arr:
        print ('Counts for class ', uniq_class_arr[_class], ': ', counts[_class])

def extract_train_for_autoML(assets):
    X_train = []
    y_train = []
    for asset in assets:
        for label in asset["labels"]:
            if label["labelType"] == "DEFAULT":
                jsonResponse = json.loads(label["jsonResponse"])
                X_train.append(asset["content"])
                y_train.append(converter_name_to_label[jsonResponse["categories"][0]["name"]])
    return X_train, y_train

def escape_content(str):
    return str.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\\$', "$")

    
def load_dataset_and_predictions(data_path, figure_path):
    X_train, y_train, X_test, y_test = load_imdb_dataset(data_path)
    
    #Explore dataset
    print_infos_dataset(X_train,y_train,X_test,y_test)
    plot_sample_length_distribution(figure_path, X_train)
    plot_most_frequent_words_or_ngrams(figure_path, X_train)


    return X_train, y_train, X_test, y_test

def automl_train_and_predict(X_train, y_train, X_to_be_predicted, y_to_be_predicted):
    x_train, x_to_be_predicted = ngram_vectorize(X_train, y_train, X_to_be_predicted)

    tmp_folder = './autosklearn_parallel_1_example_tmp'
    output_folder = './autosklearn_parallel_1_example_out'

    cls = autosklearn.classification.AutoSklearnClassifier(n_jobs =4, time_left_for_this_task = 60,
                                                           per_run_time_limit=15,
                                                           tmp_folder=tmp_folder,
                                                           output_folder=output_folder,
                                                           seed=10
                                                        )
    cls.fit(x_train, y_train)
    assert x_train.shape[1] == x_to_be_predicted.shape[1]
    predictions = cls.predict(x_to_be_predicted)
    print("Accuracy: {}".format(accuracy_score(y_to_be_predicted, predictions)))
    print("Precision|Recall|F1Score|Support: {}".format(precision_recall_fscore_support(y_to_be_predicted, predictions)))
    shutil.rmtree(tmp_folder)
    shutil.rmtree(output_folder)
    return predictions



@click.command()
@click.option('--graphql_client', default='https://cloud.kili-technology.com/api/label/graphql', help='Endpoint of GraphQL client')
def main(graphql_client):
    path_gz = download_dataset()
    data_root_path = extract_dataset(path_gz)
    data_path = os.path.join(data_root_path, 'aclImdb')
    plot_path = os.path.jy_train_originoin(data_root_path, 'plots')
    if not os.path.exists(plot_path):
        os.mkdir(plot_path)

    mail = input('Enter Email: ')
    password = getpass.getpass('Enter password for user {}:'.format(mail))
    client, user_id = authenticate( mail, password, api_endpoint=graphql_client)
    project_id = input('Enter project id: ')

    X_train_origin, y_train_origin, X_test, y_test = load_dataset_and_predictions(data_path, plot_path)

    # Push dataset on project
    converter_external_id_to_id = {}
    for external_id, content in enumerate(tqdm(X_test[:300])):
        # Insert asset
        append_to_dataset(
            client, project_id, escape_content(content), external_id)
        asset = get_assets_by_external_id(client, project_id, external_id)
        asset_id = asset[0]['id']
        converter_external_id_to_id[external_id] = asset_id


    # Check and load new predictions
    STOP_CONDITION = True
    while STOP_CONDITION:
        print("Export assets and labels...")
        assets = export_assets(client, project_id)
        print("Done.\n")
        X_train, y_train = extract_train_for_autoML(assets)

        if len(X_train)>5 and len(X_train)<30:
            print("Online Learning is on its way...")
            predictions = automl_train_and_predict(X_train, y_train, X_test[:300], y_test[:300])
            # Insert pre-annotations
            for external_id, prediction in enumerate(tqdm(predictions)):
                json_response = {"categories":[{"name":converter_label_to_name[prediction],"confidence":100}]}
                create_prediction(client, converter_external_id_to_id[external_id], json_response)
            print("Done.\n")
        elif len(X_train)>=30:
            print("Online Learning is on its way...")
            predictions = automl_train_and_predict(X_train_origin[:2000], y_train_origin[:2000], X_test[:300], y_test[:300])
            # Insert pre-annotations
            for external_id, prediction in enumerate(tqdm(predictions)):
                json_response = {"categories": [{"name": converter_label_to_name[prediction], "confidence": 100}]}
                create_prediction(client, converter_external_id_to_id[external_id], json_response)
            print("Done.\n")


if __name__ == '__main__':
    main()
