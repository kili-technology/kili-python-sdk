import os
import getpass
from tqdm import tqdm
import click

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
from kili.mutations.label import create_prediction
from kili.queries.asset import get_assets_by_external_id


NGRAM_RANGE = (1, 2)
TOP_K = 20000
TOKEN_MODE = 'word'
MIN_DOC_FREQ = 2

def shuffle(X, y):
    perm = np.random.permutation(len(X))
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


def escape_content(str):
    return str.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\\$', "$")

    
def load_dataset_and_predictions(data_path, figure_path):
    X_train, y_train, X_test, y_test = load_imdb_dataset(data_path)
    
    #Explore dataset
    print_infos_dataset(X_train,y_train,X_test,y_test)
    plot_sample_length_distribution(figure_path, X_train)
    plot_most_frequent_words_or_ngrams(figure_path, X_train)
    
    x_train, x_test = ngram_vectorize(X_train, y_train, X_test)
    cls = autosklearn.classification.AutoSklearnClassifier(n_jobs =4, time_left_for_this_task = 3600,
                                                           per_run_time_limit=800,
                                                           tmp_folder='./autosklearn_parallel_1_example_tmp',
                                            output_folder='./autosklearn_parallel_1_example_out')
    cls.fit(x_train, y_train)
    predictions = cls.predict(x_test)
    print("Accuracy: {}".format(accuracy_score(y_test, predictions)))
    print("Precision|Recall|F1Score|Support: {}".format(precision_recall_fscore_support(y_test, predictions)))
    return X_test, predictions

    


@click.command()
@click.option('--mail', help='Client mail', required=True)
@click.option('--graphql_client', default='http://localhost:4000/graphql', help='Endpoint of GraphQL client')
@click.option('--data_path', default='./aclImdb/', help='Path to IMDB dataset')
@click.option('--figure_path', default='./', help='Path to figures')
def main(mail, graphql_client, data_path, figure_path):
    password = getpass.getpass(f'Enter password for user "{mail}":')
    X_test, predictions = load_dataset_and_predictions(data_path, figure_path)

    client, user_id = authenticate( mail, password, api_endpoint=graphql_client)
    project_id = input('Enter project id: ')

    converter_label_to_name = {0:"NEGATIVE", 1:"POSITIVE"}

    for external_id, content in enumerate(tqdm(X_test)):
        # Insert asset
        append_to_dataset(
            client, project_id, escape_content(content), external_id)
        asset = get_assets_by_external_id(client, project_id, external_id)
        asset_id = asset[0]['id']

        # Insert pre-annotations
        json_response = {"categories":[{"name":converter_label_to_name[predictions[external_id]],"confidence":100}]}
        create_prediction(client, asset_id, json_response)


if __name__ == '__main__':
    main()