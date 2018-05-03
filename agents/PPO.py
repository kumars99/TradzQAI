from tensorforce.agents import PPOAgent

from collections import deque
import pandas as pd

class PPO(PPOAgent):

    def __init__(self, state_size, env=None, is_eval=False):
        self.state_size = state_size
        self.action_size = 3
        self._memory_size = 1000
        self._memory = deque(maxlen=1000)
        self.inventory = pd.DataFrame(columns=['Price', 'POS', 'Order'])
        self.is_eval = is_eval
        self.learning_rate = env.hyperparameters['learning_rate']
        self.gamma = env.hyperparameters['gamma']
        self.env = env

        self.explo = dict(
            type = 'epsilon_decay',
            initial_epsilon = env.hyperparameters['epsilon'],
            final_epsilon = env.hyperparameters['epsilon_min']
        )

        self._update_mode = dict(
            unit = 'timesteps',
            batch_size = self.env.batch_size,
            frequency = self.env.batch_size // 8
        )

        self._summarizer = dict(
            directory="./board/",
            steps=100,
            labels=['configuration',
                    'gradients_scalar',
                    'regularization',
                    'inputs',
                    'losses',
                    'variables']
        )

        self._mem=dict(
            type='latest',
            include_next_states=True,
            capacity=((len(self.env.data) - 1) * self.env.batch_size)
        )

        PPOAgent.__init__(self,
                           states = dict(type='float', shape=self.state_size.shape),
                           actions = dict(type='int', num_actions=self.action_size),
                           network = self.get_network(),
                           step_optimizer = self.get_optimizer(),
                           actions_exploration = self.explo,
                           update_mode = self._update_mode,
                           batching_capacity = self._memory_size)

        self._load_model()

    def build_model(self):
        pass

    def expReplay(self, reward, done):
        self.observe(reward=reward, terminal=done)

    def get_network(self):
        network = [dict(type='dense', size=32, activation='relu'),
                   dict(type='dense', size=32, activation='relu'),
                   dict(type='internal_lstm', size=32)]
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
