import numpy as mp
import pandas as pd
import matplotlib.pyplot as plt
import math, time
import os
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.layers.recurrent import LSTM
from keras.models import load_model
from utils import *


def build_model(layers):
    dropout = 0.2
    model = Sequential()
    model.add(LSTM(256, input_shape=(layers[1], layers[0]), return_sequences=True))
    model.add(Dropout(dropout))
    model.add(LSTM(128, input_shape=(layers[1], layers[0]),return_sequences=False))
    model.add(Dropout(dropout))
    model.add(Dense(16, kernel_initializer='RandomNormal', activation='relu'))
    model.add(Dense(1, kernel_initializer='RandomNormal', activation='linear'))
    model.compile(loss='mse', optimizer='adam', metrics=['accuracy'])
    return model

def set_RNN(path_row, epochs):
    #path_row = "dataset/DAX30/dax30_2011/DAT_ASCII_GRXEUR_M1_2011.csv"
    names = ['Time', 'Open', 'High', 'Low', 'Close', '']
    path_model = "saved_models/DAX30_3.HDF5"
    #epochs = 20
    predict = 10
    data = open_row(path_row, names)
    #col_names = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    #data = open_row(path_row, col_names)
    #data = data
    data.drop(data.columns[[0, 3, 5]], axis=1, inplace=True)
    data['Open'] /=10000
    data['High'] /=10000
    data['Close'] /=10000
    X_train, y_train, X_test, y_test = reshape_data(data[::-1], predict)
    model = load_m(path_model, predict)
    model = training(model, X_train, y_train, X_test, y_test, epochs)
    save_m(model, path_model)
    p = model.predict(X_test)
    print("prediction :", p, "test :", y_test)
    #print(path_row)
    #plt.plot(p, color='green', label='predictions')
    #plt.plot(y_test, color='red', label='y_test')
    #plt.legend(loc='upper left')
    #plt.show()

def load_m(model_path, predict):
    if os.path.isfile(model_path):
        model = load_model(model_path)
    else:
        model = build_model([3, predict, 1])
        open(model_path, 'w')
    return model

def save_m(model, model_path):
    model.save(model_path)

def reshape_data(data, len_predict):
    amount_of_features = len(data.columns)
    datas = data.as_matrix()
    seq = len_predict + 1
    result = []
    for index in range(len(datas) - len_predict):
        result.append(datas[index: index + seq])
    result = np.array(result)
    row = round(0.9 * result.shape[0])
    train = result[:int(row)]
    x_train = train[:, :-1]
    y_train = train[:, -1][:, -1]
    x_test = result[int(row):, :-1]
    y_test = result[int(row):, -1][:, -1]
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], amount_of_features))
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], amount_of_features))
    return [x_train, y_train, x_test, y_test]

def training(model, X_train, y_train, X_test, y_test, epochs):
    model.fit(X_train, y_train, batch_size = 512, epochs = epochs, validation_split = 0.1, verbose = 1)
    trainScore = model.evaluate(X_train, y_train, verbose=0)
    print('Train Score : %.4f MSE MSE (%.4f RMSE)' % (trainScore[0], math.sqrt(trainScore[0])))
    testScore = model.evaluate(X_test, y_test, verbose=0)
    print('Test Score : %.4f MSE MSE (%.4f RMSE)' % (testScore[0], math.sqrt(testScore[0])))
    return model

#def predict():

def full_train():
    i = 0
    while i < 7:
        path_row = "dataset/DAX30/dax30_201"+str(i)+"/DAT_ASCII_GRXEUR_M1_201"+str(i)+".csv"
        set_RNN(path_row, 20)
        i += 1

    i = 1
    while i < 8:
        path_row = "dataset/DAX30/dax30_2017_0"+str(i)+"/DAT_ASCII_GRXEUR_M1_20170"+str(i)+".csv"
        set_RNN(path_row, 50)
        i += 1

full_train()

