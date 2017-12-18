import keras

from keras.models import Sequential
from keras.layers import Dense, PReLU, CuDNNLSTM, Flatten, Reshape, Dropout
from keras.optimizers import Adam

import os
import time

import numpy as np
import random
from collections import deque

from core.environnement import *

class DDQN:
    def __init__(self, state_size, env=None, is_eval=False, model_name=""):
        self.state_size = state_size # normalized previous days
        self.action_size = 3 # sit, buy, sell
        self.memory = deque(maxlen=1000)
        columns = ['Price', 'POS', 'Order']
        self.inventory = pd.DataFrame(columns=columns)
        self.mode = ""
        self.model_name = model_name
        self.is_eval = is_eval

        self.env = env

        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995

        if os.path.exists("models/" + model_name):
            self.model = load_model("models/" + model_name)
        else:
            self.model = self._model()
            self.target_model = self._model()

    def _model(self):
        model = Sequential()
        model.add(Dense(32, input_shape=self.state_size, activation='relu'))
        model.add(Dense(32, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss="mse", optimizer=Adam(lr=0.001))
        return model

    def update_target_model(self):
        self.target_model.set_weights(self.model.get_weights())

    def expReplay(self, batch_size):
        mini_batch = []
        l = len(self.memory)
        for i in range(l - batch_size + 1, l):
            mini_batch.append(self.memory[i])
        
        for state, action, reward, next_state, done in mini_batch:
            target = self.predict(state)
            if done:
                target[0][action] = reward
            else:
                a = self.model.predict(next_state)[0]
                t = self.target_model.predict(next_state)[0]
                target[0][action] = reward + self.gamma * t[np.argmax(a)]

            self.model.fit(state, target, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= epsilon_decay
