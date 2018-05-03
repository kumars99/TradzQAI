from .saver import Saver

import time

from collections import deque

class Logger(Saver):

    def __init__(self):

        Saver.__init__(self)

        self.log_path = "logs/"


        self.logs = {}
        self.id = {}
        self.current_index = {}

        self.conf = ""
        self.new_logs(self.name)
        self.logs[self.name].append(time.strftime("%Y:%m:%d %H:%M:%S") + \
                        " " + '{:010d}'.format(self.id[self.name]) + " " \
                        + str("Starting logs") + "\n")
        self.id[self.name] += 1



    def new_logs(self, name):
        '''
        name : name as string
        '''
        if type(name) is str:
            self.logs[name] = []
            self.id[name] = 0
            self.current_index[name] = 0
            self.log_file[name] = None
            if self.files_checked is True:
                self.load_log(name)
        else:
            raise ValueError("name should be a string")

    def _save_conf(self, env):
        conf = self.conf

        conf += "#### Configuration file ####" +"\n\n"
        conf += "Configuration file created : "+time.strftime("%Y / %m / %d") +"\n"
        conf += "Software name : "+str(env.name) +"\n"
        conf += "Version : "+str(env.version) +"\n\n"

        conf += "#### Model settings ####" +"\n\n"
        conf += "Model name : "+str(env.model_name) +"\n\n"

        conf += "#### Hyperparameters ####" +"\n\n"
        conf += "Learning rate : " +str(env.hyperparameters['learning_rate']) +"\n"

        if env.model_name == "DDQN" or env.model_name == "DDRQN":
            conf += "Update rate : " +str(env.hyperparameters['update_rate']) +"\n"

        conf += "Gamma : "+str(env.hyperparameters['gamma']) +"\n"
        conf += "Epsilon : "+str(env.hyperparameters['epsilon']) +"\n\n"

        conf += "#### Environnement settings ####" +"\n\n"
        conf += "Stock name : "+str(env.stock_name) +"\n"
        conf += "Episode : " +str(env.episode_count) +"\n"
        conf += "Window size : " +str(env.window_size) +"\n"
        conf += "Batch size : " +str(env.batch_size) +"\n"
        conf += "Contract price : " +str(env.contract_settings['contract_price']) +"\n"
        conf += "Pip value : " +str(env.contract_settings['pip_value']) +"\n"
        conf += "Spread : " +str(env.contract_settings['spread']) +"\n\n"

        conf += "#### Wallet and risk settings ####" +"\n\n"
        conf += "Capital : " +str(env.wallet.settings['capital']) +"\n"
        conf += "Exposure : "+str(env.wallet.risk_managment['exposure']) +"\n"
        conf += "Max pip loss : " +str(env.wallet.risk_managment['stop_loss']) +"\n"
        conf += "Max pos : " +str(env.wallet.risk_managment['max_pos']) +"\n"

        self._save(conf=conf)
        self._save(model_conf=conf)

    def init_saver(self, env):
        self._check(env.model_dir, self.log_path)
        self.load_log(self.name)
        self._add("Saver initialized", self.name)

    def _add(self, log, name):
        self.logs[name].append(time.strftime("%Y:%m:%d %H:%M:%S") + \
            " " + '{:010d}'.format(self.id[name]) + " " + str(log) + "\n")
        if self.log_file[name] != None:
            if self.current_index[name] < self.id[name]:
                while self.current_index[name] <= self.id[name]:
                    self._save(logs=self.logs[name][self.current_index[name]], logs_name=name)
                    self.current_index[name] += 1
            else:
                self._save(logs=self.logs[name][self.id[name]], logs_name=name)
                self.current_index[name] += 1
        self.id[name] += 1
