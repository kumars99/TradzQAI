import numpy as mp
import pandas as pd
import matplotlib.pyplot as plt
import math, time
import os
from keras.models import Sequential, load_model
from keras.layers.core import Dense, Dropout, Activation
from keras.layers import LSTM, CuDNNLSTM
import keras
from utils import *
from environnement import *

env = environnement()

class RNN():

    def __init__(self):
        self.model = None
        self.data = None
        self.path = None
        self.model_path = './models/RNN/open/DAX30_O_test2.HDF5'
        self.model_name = (self.model_path.replace("./saved_models/", "")).replace(".HDF5", "")
        self.window = 50
        self.predict = None
        self.tbCallback = []
        self.epochs = 0

    def Callback(self):
        new = keras.callbacks.ModelCheckpoint(self.model_path, monitor='val_loss', verbose=0, save_best_only=True, save_weights_only=False, mode='auto', period=1)
        self.tbCallback.append(new)
        #new = keras.callbacks.TensorBoard(log_dir="./Graph/"+str(self.model_name)+"/s", histogram_freq=0, write_graph=True, write_images=False, write_grads=False)
        #new.set_model(self.model)
        #self.tbCallback.append(new)

    def get_data(self, f):
        names = ['Time', 'Open', 'High', 'Low', 'Close', '']
        self.data = check_10s(self.path, f)
        self.data['Open'] /= 10000
        self.data['High'] /= 10000
        self.data['Close'] /= 10000
        self.data['Low'] /= 10000
        self.last = self.data.copy(deep=True)
        self.data.drop(self.data.columns[[0, 1]], axis=1, inplace=True)
        self.last.drop(self.last.columns[[0, 2, 3, 4]], axis=1, inplace=True)
        self.data = self.data.join(self.last)
        return reshape_data(self.data[::-1], self.window)

    def get_model(self):
        self.model = load_m(self.model_path, self.window)
        return self.model

    def predict(self):
        self.predict = self.model.predict(self.data)
        return self.predict

    def train(self, X_train, y_train, X_test, y_test):
        self.model.fit(X_train, y_train, batch_size = 64, epochs = self.epochs, validation_split = 0.2, verbose = 1)
        trainScore = self.model.evaluate(X_train, y_train, verbose=0)
        print('Train Score : %.4f MSE MSE (%.4f RMSE)' % (trainScore[0], math.sqrt(trainScore[0])))
        testScore = self.model.evaluate(X_test, y_test, verbose=0)
        print('Test Score : %.4f MSE MSE (%.4f RMSE)' % (testScore[0], math.sqrt(testScore[0])))



def build_model(layers):
    dropout = 0.3
    model = Sequential()
    model.add(CuDNNLSTM(256, input_shape=(layers[1], layers[0]), return_sequences=True))
    model.add(Dropout(dropout))
    model.add(CuDNNLSTM(128, input_shape=(layers[1], layers[0]),return_sequences=False))
    model.add(Dropout(dropout))
    model.add(Dense(16, kernel_initializer='RandomUniform', activation='relu'))
    model.add(Dense(1, kernel_initializer='RandomUniform', activation='linear'))
    model.compile(loss='mse', optimizer='adam', metrics=['accuracy'])
    return model

def get_accuracy(predict, model, X_test, y_test):
    ret = model.predict(X_test)
    predict = len(ret) - predict - 1
    i = 0
    acc = 0
    accu = 0
    lower = 100000
    higher = 0
    while i < len(ret) - 1:
        i += 1
        acc += ret[i] - y_test[i]
        accu += ret[i] / y_test[i]
        predict += 1
    accu /= i
    acc /= i
    print ("Accuracy : ", accu)
    print ("Ecart pips moyen :", acc * 10000)
    return ret

def load_m(model_path, predict):
    if os.path.isfile(model_path):
        model = load_model(model_path)
    else:
        model = build_model([4, predict, 1])
        open(model_path, 'w')
        save_m(model, model_path)
    return model

def save_m(model, model_path):
    model.save(model_path)

def reshape_data(data, len_predict):
    amount_of_features = len(data.columns)
    datas = data.as_matrix()
    seq = len_predict + 1
    r = []
    for index in range(len(datas) - len_predict):
        r.append(datas[index: index + seq])
    result = np.array(r)
    row = round(0.9 * result.shape[0])
    train = result[:int(row)]
    x_train = train[:, :-1]
    y_train = train[:, -1][:, -1]
    x_test = result[int(row):, :-1]
    y_test = result[int(row):, -1][:, -1]
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], amount_of_features))
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], amount_of_features))
    return [x_train, y_train, x_test, y_test]

def full_run():
    new = RNN()
    new.get_model()
    #new.Callback()
    new.path = "./dataset/DAX30/Tick"
    new.epochs = 10
    dirs = os.listdir(new.path)
    data = None
    dirs.sort()
    for d in dirs:
        new.path = "./dataset/DAX30/Tick"
        n = str(new.path)+"/"+str(d)
        path = os.listdir(n)
        path.sort()
        for p in path:
            new.path = "./dataset/DAX30/Tick"
            n = str(new.path)+"/"+str(d) +"/"+str(p)
            files = os.listdir(n)
            for f in files:
                if ".csv" in f:
                    new.path = n + "/" + str(f)
                    check_10s(new.path, f)
                    '''
                    X_train, y_train, X_test, y_test = new.get_data(f)
                    new.train(X_train, y_train, X_test, y_test)
                    save_m(new.model, new.model_path)
                    ret = get_accuracy(new.window, new.get_model(), X_test, y_test)
                    plt.plot(ret, color='green', label='predictions')
                    plt.plot(y_test, color='red', label='y_test')
                    plt.legend(loc='upper left')
                    plt.show()
                    '''
                    #new.tbCallback[1] = keras.callbacks.TensorBoard(log_dir="./Graph/"+str(new.model_name+"/"+str(i)), histogram_freq=1, write_graph=False, write_images=False, write_grads=True)
full_run()
