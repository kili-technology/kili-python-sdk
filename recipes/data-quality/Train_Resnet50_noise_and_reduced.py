# coding: utf-8

# Examples of execution : 
# python3 Train_Resnet50_with_noise.py --epochs 200 --noise 20 --percentage 80
# To save log : 
# python3 Train_Resnet50_with_noise.py --epochs 200 --noise 20 --percentage 80 > noise20_percentage80.log

# tensorflow 2.3.0
# cuda 10.1

import os
os.environ["CUDA_VISIBLE_DEVICES"]="0"

import tensorflow as tf
config = tf.compat.v1.ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.5
session = tf.compat.v1.Session(config=config)

import argparse
from argparse import Namespace
import numpy as np 
from tensorflow.keras import applications
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Dropout,GlobalAveragePooling2D
from tensorflow.keras import datasets
from tensorflow.keras.optimizers import SGD, Adam

parser = argparse.ArgumentParser(description='ResNet training with noise.')

parser.add_argument('--epochs', default=200, type=int)
parser.add_argument('--noise', default=0, type=int, 
                    help='The percentage of the dataset with noisy label '
                    '(number between 0 to 100)')
parser.add_argument('--percentage', default=0, type=int, 
                    help='The percentage of the dataset with noisy label '
                    '(number between 0 to 100)')

def load_dataset(percentage=50.0, noisy_percentage = 0.0):
    (train_images, train_labels), (test_images, test_labels) = datasets.cifar10.load_data()
    
    number_classes = 10
    
    ### Reduce size of dataset
    X_train_classes = []
    for i in range(number_classes):
        X_train_classes.append(train_images[np.where(train_labels == [i])[0]])  
    
    y_train_classes = []
    for i in range(number_classes):
        y_train_classes.append(i*np.ones(len(X_train_classes[i]), dtype=np.int8))
    
    y_train_subset_temp = []
    y_train_subset = []
    
    X_train_subset_temp = []
    X_train_subset = []
    for i in range(number_classes):
        number= int(len(y_train_classes[i])*(percentage/100))
        
        X_train_i_subset, X_train_i_delete = np.split(X_train_classes[i], [number])
        X_train_subset_temp.append(X_train_i_subset)

        
        y_train_i_subset, y_train_i_delete = np.split(y_train_classes[i], [number])
        y_train_subset_temp.append(y_train_i_subset)
        y_train_subset = np.array(y_train_subset_temp).flatten()
    
    X_train_subset = np.reshape(X_train_subset_temp, (number*10,32,32,3))
    
    np.random.seed(1)
    np.random.shuffle(X_train_subset)
    np.random.seed(1)
    np.random.shuffle(y_train_subset)
    y_train = np.reshape(y_train_subset, (len(y_train_subset),1))
    
    ### Add noise to labels

    (train_images, train_labels), (test_images, test_labels) = (X_train_subset, y_train), (test_images, test_labels)
    number_classes = 10
    
    X_train_classes = []
    for i in range(number_classes):
        X_train_classes.append(train_images[np.where(train_labels == [i])[0]])  
    X_train_classes_flat = np.reshape(X_train_classes, (len(train_labels),32,32,3))
    
    y_train_classes = []
    for i in range(number_classes):
        y_train_classes.append(i*np.ones(len(X_train_classes[i]), dtype=np.int8))
     
    y_train_classes_noisy_temp = []
    y_train_classes_noisy = []
    for i in range(number_classes):
        number= int(len(y_train_classes[i])*(1-noisy_percentage/100))
        y_train_i_correct, y_train_i_noisy = np.split(y_train_classes[i], [number])
        y_train_i_noisy = np.random.choice(np.delete(np.arange(number_classes),i), len(y_train_i_noisy))
        y_train_classes_noisy_temp.append(np.concatenate((y_train_i_correct, y_train_i_noisy)))
        y_train_classes_noisy = np.array(y_train_classes_noisy_temp).flatten()
        
    np.random.seed(1)
    np.random.shuffle(X_train_classes_flat)
    np.random.seed(1)
    np.random.shuffle(y_train_classes_noisy)
    y_train = np.reshape(y_train_classes_noisy, (len(y_train_classes_noisy),1))
    
    return (X_train_classes_flat, y_train), (test_images, test_labels)

def convert_to_one_hot(Y, C):
    Y = np.eye(C)[Y.reshape(-1)].T
    return Y

def main(args):
    classes = [0,1,2,3,4,5,6,7,8,9]
    (X_train_orig, Y_train_orig), (X_test_orig, Y_test_orig)  = load_dataset(noisy_percentage = args.noise, percentage = args.percentage)

    # Normalize image vectors
    X_train = X_train_orig/255.
    X_test = X_test_orig/255.

    # Convert training and test labels to one hot matrices
    Y_train_orig = np.reshape(Y_train_orig, (len(Y_train_orig)))
    Y_test_orig = np.reshape(Y_test_orig, (len(Y_test_orig)))
    Y_train = convert_to_one_hot(Y_train_orig, len(classes)).T
    Y_test = convert_to_one_hot(Y_test_orig, len(classes)).T

    print ("Noise = " + str(args.noise))
    print ("Percentage of dataset = " + str(args.percentage))
    print ("number of training examples = " + str(X_train.shape[0]))
    print ("number of test examples = " + str(X_test.shape[0]))
    print ("X_train shape: " + str(X_train.shape))
    print ("Y_train shape: " + str(Y_train.shape))
    print ("X_test shape: " + str(X_test.shape))
    print ("Y_test shape: " + str(Y_test.shape))

    img_height,img_width = 32,32
    num_classes = len(classes)
    #If imagenet weights are being loaded, 
    #input must have a static square shape (one of (128, 128), (160, 160), (192, 192), or (224, 224))
    base_model = applications.resnet50.ResNet50(weights= None, include_top=False, input_shape= (img_height,img_width,3))

    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dropout(0.7)(x)
    predictions = Dense(num_classes, activation= 'softmax')(x)
    model = Model(inputs = base_model.input, outputs = predictions)

    # sgd = SGD(lr=lrate, momentum=0.9, decay=decay, nesterov=False)
    adam = Adam(lr=0.0001)
    model.compile(optimizer= adam, loss='categorical_crossentropy', metrics=['accuracy'])

    model.fit(X_train, Y_train, epochs = args.epochs, batch_size = 64, validation_data=(X_test,Y_test))

    if not os.path.exists("Models"):
        os.makedirs('Models')
    filename = 'noise_' + str(args.noise) + '__percentageReduced_' + str(args.percentage) + '__epochs_' + str(args.epochs)
    model.save('./Models/' + filename)

    accuracy = model.history.history['val_accuracy']
    print('Filename:' + filename)
    print('Test accuracy by epochs:')
    print(accuracy)
    print('Train accuracy by epochs:')
    print(model.history.history['accuracy'])
    print ("####################################\n\n")

if __name__ == '__main__':
    arg_parser = parser.parse_args()
    print(arg_parser)
    main(arg_parser)

