from tensorforce.agents import DQNAgent

from collections import deque
import pandas as pd

class DQN(DQNAgent):

    def __init__(self, state_size, env=None, is_eval=False):
        self.state_size = state_size
        self.action_size = 3
        self.memory_size = 1000
        self._memory = deque(maxlen=1000)
        self.inventory = pd.DataFrame(columns=['Price', 'POS', 'Order'])
        self.is_eval = is_eval
        self.learning_rate = env.learning_rate
        self.gamma = env.gamma
        self.env = env

        self.up = dict(batch_size = self.env.batch_size,
                       frequency = self.env.batch_size)

        DQNAgent.__init__(self,
                           states=dict(type='float', shape=self.state_size.shape),
                           actions=dict(type='int', num_actions=self.action_size),
                           network=self.get_network(),
                           update_mode=self.up,
                           batching_capacity=self.memory_size,
                           learning_rate=self.learning_rate,
                           discount=self.gamma)

        self._load_model()

    def build_model(self):
        pass

    def expReplay(self, reward, terminal):
        self.observe(reward=reward, terminal=terminal)

    def get_network(self):
        network = [dict(type='dense', size=64),
                   dict(type='dense', size=64)]
        return network

    def get_optimizer(self):
        optimizer = dict(type='adam', learning_rate=self.learning_rate)
        return optimizer

    def _save_model(self):
        if self.env.logger.model_file_name == "":
            self.env.logger.model_file_name = self.env.model_name + "_" + self.env.stock_name
            self.env.logger.model_file_path += self.env.logger.model_file_name
        self.save_model(directory=self.env.logger.model_file_path, append_timestep=True)

    def _load_model(self):
        try:
            self.restore_model(self.env.logger.model_direct)
        except:
            pass
