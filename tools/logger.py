from .saver import Saver
from .utils import str2bool

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
        self._add("Starting logs", self.name)
        '''
        self.logs[self.name].append(time.strftime("%Y:%m:%d %H:%M:%S") + \
                        " " + '{:06d}'.format(self.id[self.name]) + " " \
                        + str("Starting logs") + "\n")

        self.id[self.name] += 1
        '''

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
        conf += "Configuration file created : "+ time.strftime("%Y / %m / %d") +"\n"
        conf += "Software name : "+str(env.name) +"\n"
        conf += "Version : "+str(env.version) +"\n\n"

        conf += "#### Agent settings ####" +"\n\n"
        conf += "Agent name : "+str(env.model_name) +"\n\n"

        conf += "#### Hyperparameters ####" +"\n\n"
        conf += "Learning rate : " +str(env.hyperparameters['learning_rate']) +"\n"
        conf += "Gamma : "+str(env.hyperparameters['gamma']) +"\n"
        conf += "Epsilon : "+str(env.hyperparameters['epsilon']) +"\n"
        conf += "Epsilon min : "+str(env.hyperparameters['epsilon_min']) +"\n\n"

        conf += "#### Environnement settings ####" +"\n\n"
        conf += "Stock name : "+str(env.stock_name) +"\n"
        conf += "Episode : " +str(env.episode_count) +"\n"
        conf += "Window size : " +str(env.window_size) +"\n"
        conf += "Batch size : " +str(env.batch_size) +"\n\n"

        conf += "#### Contract settings ####" +"\n\n"
        conf += "Allow short : " + str(env.contract_settings['allow_short']) +"\n"
        conf += "Contract price : " +str(env.contract_settings['contract_price']) +"\n"
        conf += "Pip value : " +str(env.contract_settings['pip_value']) +"\n"
        conf += "Spread : " +str(env.contract_settings['spread']) +"\n\n"

        conf += "#### Wallet and risk settings ####" +"\n\n"
        conf += "Capital : " +str(env.wallet.settings['capital']) +"\n"
        conf += "Exposure : "+str(env.wallet.risk_managment['exposure']) +"\n"
        conf += "Stop loss : " +str(env.wallet.risk_managment['stop_loss']) +"\n"
        conf += "Max pos : " +str(env.wallet.risk_managment['max_pos']) +"\n"

        self._save(conf=conf)

    def _load_conf(self, env):

        self.load_conf()
        try:
            lines = self.conf_file.read()
            lines = lines.split("\n")
        except:
            lines = ""
        for line in lines:
            if "Agent name" in line:
                env.model_name = (line.split(":")[1]).replace(" ", "")
            if "Learning rate" in line:
                env.hyperparameters['learning_rate'] = float((line.split(":")[1]).replace(" ", ""))
            if "Gamma" in line:
                env.hyperparameters['gamma'] = float((line.split(":")[1]).replace(" ", ""))
            if "Espilon" in line:
                env.hyperparameters['epsilon'] = float((line.split(":")[1]).replace(" ", ""))
            if "Espilon min" in line:
                env.hyperparameters['epsilon_min'] = float((line.split(":")[1]).replace(" ", ""))
            if "Stock name" in line:
                env.stock_name = (line.split(":")[1]).replace(" ", "")
            if "Window size" in line:
                env.window_size = int((line.split(":")[1]).replace(" ", ""))
            if "Episode" in line:
                env.episode_count = int((line.split(":")[1]).replace(" ", ""))
            if "Batch size" in line:
                env.batch_size = int((line.split(":")[1]).replace(" ", ""))
            if "Contract price" in line:
                env.contract_settings['contract_price'] = int((line.split(":")[1]).replace(" ", ""))
            if "Pip value" in line:
                env.contract_settings['pip_value'] = int((line.split(":")[1]).replace(" ", ""))
            if "Spread" in line:
                env.contract_settings['spread'] = float((line.split(":")[1]).replace(" ", ""))
            if "Allow short" in line:
                env.contract_settings['allow_short'] = str2bool((line.split(":")[1]).replace(" ", ""))
            if "Capital" in line:
                env.wallet.settings['capital'] = int((line.split(":")[1]).replace(" ", ""))
                env.wallet.settings['saved_capital'] = env.wallet.settings['capital']
                env.wallet.settings['usable_margin'] = env.wallet.settings['capital']
            if "Exposure" in line:
                env.wallet.risk_managment['exposure'] = float((line.split(":")[1]).replace(" ", ""))
            if "Stop loss" in line:
                env.wallet.risk_managment['stop_loss'] = int((line.split(":")[1]).replace(" ", ""))
            if "Max pos" in line:
                env.wallet.risk_managment['max_pos'] = int((line.split(":")[1]).replace(" ", ""))
        env.model_dir = env.model_name + "_" + env.stock_name.split("_")[0]
        self.conf_file.close()

    def init_saver(self, env):
        self._check(env.model_dir, self.log_path, env.settings)
        self.load_log(self.name)
        self._add("Saver initialized", self.name)

    def _add(self, log, name):
        self.logs[name].append(time.strftime("%Y:%m:%d %H:%M:%S") + \
            " " + '{:06d}'.format(self.id[name]) + " " + str(log) + "\n")
        if self.log_file[name] != None:
            if self.current_index[name] < self.id[name]:
                while self.current_index[name] <= self.id[name]:
                    self._save(logs=self.logs[name][self.current_index[name]], logs_name=name)
                    self.current_index[name] += 1
            else:
                self._save(logs=self.logs[name][self.id[name]], logs_name=name)
                self.current_index[name] += 1
        self.id[name] += 1
