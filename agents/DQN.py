from tensorforce.agents import DQNAgent

from collections import deque
import pandas as pd

class DQN(DQNAgent):

    def __init__(self, state_size, env=None, is_eval=False):

        self.state_size = state_size
        self.action_size = 3
        self._memory_size = 1000
        self._memory = deque(maxlen=1000)
        self.is_eval = is_eval
        self.learning_rate = env.hyperparameters['learning_rate']
        self.gamma = env.hyperparameters['gamma']
        self.env = env

        self.explo = dict(
            type = 'epsilon_anneal',
            initial_epsilon = env.hyperparameters['epsilon'],
            final_epsilon = env.hyperparameters['epsilon_min']
        )

        self._update_mode = dict(
            unit = 'timesteps',
            batch_size = self.env.batch_size,
            frequency = self.env.batch_size // 8
        )

        self._summarizer = dict(
            directory=self.env.logger.model_direct + "/board/",
            steps=self.env.batch_size,
            labels=['losses']
        )


        DQNAgent.__init__(self,
                           states = dict(type='float', shape=self.state_size.shape),
                           actions = dict(type='int', num_actions=self.action_size),
                           network = self.get_network(),
                           optimizer = self.get_optimizer(),
                           actions_exploration = self.explo,
                           update_mode = self._update_mode,
                           double_q_model = True,
                           batching_capacity = self._memory_size)
                           #summarizer=self._summarizer)

        self._load_model()

    def build_model(self):
        pass

    def expReplay(self, reward, done):
        self.observe(reward=reward, terminal=done)
        '''
        mini_batch = []
        l = len(self._memory)
        for i in range(l - self.env.batch_size + 1, l):
            mini_batch.append(self._memory[i])
        for state, action, reward, next_state, done in mini_batch:
            self.atomic_observe(state, action, next_state, reward, done)
        '''

    def get_network(self):
        network = [dict(type='dense', size=64, activation='relu'),
                   dict(type='dense', size=64, activation='relu')]
        return network

    def get_optimizer(self):
        optimizer = dict(type='adam', learning_rate=self.learning_rate)
        return optimizer

    def _save_model(self):
        if self.env.logger.model_file_name == "":
            self.env.logger.model_file_name = self.env.model_name + "_" + self.env.stock_name
            self.env.logger.model_file_path += self.env.logger.model_file_name
        else:
            self.env.logger.model_file_path = self.env.logger.model_file_path[:39]
        self.save_model(directory=self.env.logger.model_file_path, append_timestep=True)

    def _load_model(self):
        try:
            self.restore_model(self.env.logger.model_direct)
        except:
            pass
