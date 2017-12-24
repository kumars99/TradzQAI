import keras

import pandas as pd
import numpy as np
import random

from collections import deque
from environnement import Environnement

class Agent:

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

        self.update_rate = 1e-1
        self.learning_rate = 1e-3
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995

    def act(self, state):
        if not self.is_eval and np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)

        if self.name == "DDPG":
            return self.actor_model.predict(state)
        else:
            options = self.model.predict(state)
            return np.argmax(options[0])

    def expReplay(self, batch_size):
        mini_batch = []
        loss = []
        l = len(self.memory)
        for i in range(l - batch_size + 1, l):
            mini_batch.append(self.memory[i])
        if self.name == "DDPG":
            for state, action, reward, next_state, done in mini_batch:
                predicted_action = self.actor_model.predict(state)
                grads = self.sess.run(self.critic_grads, feed_dict={
                        self.critic_state_input: state,
                        self.critic_action_input: predicted_action})[0]
                self.sess.run(self.optimize, feed_dict={
                        self.actor_state_input: state,
                        self.actor_critic_grad: grads})
                if not done:
                    target_action = self.target_actor_model.predict(next_state)
                    future_reward = self.target_critic_model.predict(
                                    [next_state, target_action])[0][0]
                    reward += self.gamma * future_reward
                loss.append(self.critic_model.fit([state, action],
                                      reward,
                                      epochs=1,
                                      verbose=0)
                            .history['loss'])

        else:
            for state, action, reward, next_state, done in mini_batch:
                target = self.model.predict(state)
                if done:
                    target[0][action] = reward
                else:
                    if "DQN" == self.name or "DRQN" == self.name:
                        target[0][action] = reward + self.gamma * np.amax(self.model.predict(next_state)[0])
                    elif "DDQN" == self.name or "DDRQN" == self.name:
                        a = self.model.predict(next_state)[0]
                        t = self.target_model.predict(next_state)[0]
                        target[0][action] = reward + self.gamma * t[np.argmax(a)]

                loss.append(self.model.fit(state,
                                           target,
                                           epochs=1,
                                           verbose=0)
                            .history['loss'])
                if self.epsilon > self.epsilon_min:
                    self.epsilon *= self.epsilon_decay
        return np.average(loss)


    def _save_model(self):
        if self.env.logger.model_file_name is None:
            self.env.logger.model_file_name = self.name + "_" + self.env.stock_name
            self.env.logger.model_file_path = self.env.logger.model_file_path +self.env.logger.model_file_name
        
        self.model.save(self.env.logger.model_file_path)

    def _load_model(self):
        self.model = self.env.logger._load()