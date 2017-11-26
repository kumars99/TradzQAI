import keras
from keras.models import Sequential
from keras.models import load_model
from keras.layers import Dense, PReLU, CuDNNGRU
from keras.optimizers import Adam
import os

import numpy as np
import random
from collections import deque

class Agent:
    def __init__(self, state_size, is_eval=False, model_name=""):
        self.state_size = state_size # normalized previous days
        self.action_size = 3 # sit, buy, sell
        self.memory = deque(maxlen=1000)
        self.inventory = None
        self.mode = ""
        self.model_name = model_name
        self.is_eval = is_eval

        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995

        if os.path.exists("models/" + model_name):
            print ("Model loaded")
            self.model = load_model("models/" + model_name)
        else:
            print ("Model builded")
            self.model = self._model()

    def _model(self):
        model = Sequential()
        model.add(Dense(units=512, input_dim=self.state_size))
        model.add(PReLU())
        model.add(Dense(units=256))
        model.add(PReLU())
        model.add(Dense(units=128))
        model.add(PReLU())
        model.add(Dense(units=64))
        model.add(PReLU())
        model.add(Dense(units=16))
        model.add(PReLU())
        model.add(Dense(self.action_size, activation="linear"))
        model.compile(loss="mse", optimizer=Adam(lr=0.001))

        return model

    def act(self, state):
        if not self.is_eval and np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)

        options = self.model.predict(state)
        return np.argmax(options[0])

    def expReplay(self, batch_size):
        mini_batch = []
        l = len(self.memory)
        for i in range(l - batch_size + 1, l):
            mini_batch.append(self.memory[i])

        for state, action, reward, next_state, done in mini_batch:
            target = reward
            if not done:
                target = reward + self.gamma * np.amax(self.model.predict(next_state)[0])

            target_f = self.model.predict(state)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay 