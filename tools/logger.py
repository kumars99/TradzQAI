from .saver import Saver

import time

from collections import deque

class Logger(Saver):

    def __init__(self):

        Saver.__init__(self)

        self.log_path = "logs/"

        self.logs = deque(maxlen=5000)
        self.id = 0
        self.current_index = 0

        self.conf = ""

        self.logs.append(time.strftime("%Y:%m:%d %H:%M:%S") + \
                        " " + '{:010d}'.format(self.id) + " " \
                        + str("Starting logs") + "\n")
        self.id += 1

    def _save_conf(self, env):
        conf = self.conf

        conf += "#### Configuration file ####" +"\n\n"
        conf += "Configuration file created : "+time.strftime("%Y / %m / %d") +"\n"
        conf += "Software name : "+str(env.name) +"\n"
        conf += "Version : "+str(env.version) +"\n\n"

        conf += "#### Model settings ####" +"\n\n"
        conf += "Model name : "+str(env.model_name) +"\n\n"

        conf += "#### Hyperparameters ####" +"\n\n"
        conf += "Learning rate : " +str(env.learning_rate) +"\n"

        if env.model_name == "DDQN" or env.model_name == "DDRQN":
            conf += "Update rate : " +str(env.update_rate) +"\n"

        conf += "Gamma : "+str(env.gamma) +"\n"
        conf += "Epsilon : "+str(env.epsilon) +"\n\n"

        conf += "#### Environnement settings ####" +"\n\n"
        conf += "Stock name : "+str(env.stock_name) +"\n"
        conf += "Episode : " +str(env.episode_count) +"\n"
        conf += "Window size : " +str(env.window_size) +"\n"
        conf += "Batch size : " +str(env.batch_size) +"\n"
        conf += "Contract price : " +str(env.contract_price) +"\n"
        conf += "Pip value : " +str(env.pip_value) +"\n"
        conf += "Spread : " +str(env.spread) +"\n\n"

        conf += "#### Wallet and risk settings ####" +"\n\n"
        conf += "Capital : " +str(env.capital) +"\n"
        conf += "Exposure : "+str(env.exposure) +"\n"
        conf += "Max pip loss : " +str(env.max_pip_drawdown) +"\n"
        conf += "Max pos : " +str(env.max_pos) +"\n"

        self._save(conf=conf)
        self._save(model_conf=conf)

    def init_saver(self, env):
        self._check(env.model_dir, self.log_path)
        self._add("Saver initialized")

    def _add(self, log):
        self.logs.append(time.strftime("%Y:%m:%d %H:%M:%S") + \
            " " + '{:010d}'.format(self.id) + " " + str(log) + "\n")
        if self.log_file != None:
            if self.current_index < self.id:
                while self.current_index <= self.id:
                    self._save(logs=self.logs[self.current_index])
                    self.current_index += 1
            else:
                self._save(logs=self.logs[self.id])
                self.current_index += 1
        self.id += 1
