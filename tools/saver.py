from __future__ import print_function

import os
import time
import json
from deepdiff import DeepDiff
from pprint import pprint


class Saver:

    def __init__(self):

        self.root_path = "./save/"

        self.name = os.path.basename(__file__).replace(".py", "")

        self.log_file_name = {}
        self.log_file = {}
        self.log_path = ""
        self.log_file_path = {}

        self.model_file_name = ""
        self.model_file_path = ""
        self.conf_file_name = "conf.cfg"
        self.conf_file = None
        self.conf_file_path = "" + self.conf_file_name

        self.network_file_name = "network.json"
        self.network_file = None
        self.network_file_path = ""

        self.agent_file_name = "agent.json"
        self.agent_file = None
        self.agent_file_path = ""

        self.env_file_name = "environnement.json"
        self.env_file = None
        self.env_file_path = ""

        self.training_in_data_file_name = "train_in.txt"
        self.training_out_data_file_name = "train_out.txt"
        self.training_in_data_file = None
        self.training_out_data_file = None
        self.training_data_path = "training_data/"

        self.dir_id = 0

        self.model_directory = ""

        self.files_checked = False


    def check_save_dir(self):
        self._add("Checking save directory", self.name)
        if os.path.exists(self.root_path) is False:
            os.mkdir(self.root_path)

    def check_model_dir(self, model_name):
        self._add("Checking model directory", self.name)
        self.path = self.root_path + model_name + "/"
        self.model_directory = self.root_path + model_name
        if os.path.exists(self.path) is False:
            os.mkdir(self.path)

    def check_log_dir(self, log_path):
        self._add("Checking log directory", self.name)
        self.log_path = self.path + log_path
        if os.path.exists(self.log_path) is False:
            os.mkdir(self.log_path)

    def check_training_data_dir(self):
        self._add("Checking training data directory", self.name)
        self.training_data_path = "training_data/"
        tmp_path = self.path + self.training_data_path
        if os.path.exists(tmp_path) is False:
            os.mkdir(tmp_path)
        self.training_data_path = tmp_path

    def check_log_file(self, log_name):
        self._add("Checking %s logs files" % log_name, self.name)
        cdir = os.listdir(self.log_path)
        for d in cdir:
            if time.strftime("%Y_%m_%d") in d and log_name in d:
                return d
        return log_name + "_" + time.strftime("%Y_%m_%d") + ".txt"

    def check_settings_files(self):
        cdir = os.listdir(self.model_directory)
        files = 0
        for d in cdir:
            if self.network_file_name in d or \
                self.agent_file_name in d or\
                 self.env_file_name in d:
                files += 1
        self.network_file_path = self.model_directory + "/" + self.network_file_name
        self.agent_file_path = self.model_directory + "/" + self.agent_file_name
        self.env_file_path = self.model_directory + "/" + self.env_file_name
        if files == 3:
            return True
        else:
            return False

    def check_settings(self, env, agent, network):
        if self.check_settings_files() is True:
            _env, _agent, _network = self.load_settings()
            if DeepDiff(_env, env) == {} and \
                DeepDiff(_agent, agent) == {} and \
                DeepDiff(_network, network) == {}:
                return True
            else:
                return False
        else:
            return True

    def _check(self, model_name, log_path, settings):
        self.check_save_dir()
        self.check_model_dir(model_name + "_" + str(self.dir_id))
        self.check_log_dir(log_path)
        self.check_training_data_dir()
        if self.check_settings(settings['env'], settings['agent'], settings['network']) is False:
            self.dir_id += 1
            self._check(model_name, log_path, settings)
        else:
            self.save_settings(settings['env'], settings['agent'], settings['network'])
            self.files_checked = True

    def load_conf(self):
        if not os.path.exists(self.conf_file_path):
            self._add("Creating configuration file", self.name)
            open(self.conf_file_path, 'a').close()
        self._add("Loading configuration file", self.name)
        self.conf_file = open(self.conf_file_path, 'r')

    def load_settings(self):
        with open(self.env_file_path, 'r') as fp:
            env = json.load(fp=fp)
        with open(self.agent_file_path, 'r') as fp:
            agent = json.load(fp=fp)
        with open(self.network_file_path, 'r') as fp:
            network = json.load(fp=fp)
        return env, agent, network

    def load_log(self, log_name):
        self.log_file_name[log_name] = self.check_log_file(log_name)
        self.log_file_path[log_name] = self.log_path + "/" + self.log_file_name[log_name]
        self._add("Loading %s logs files" % log_name, self.name)
        self.log_file[log_name] = open(self.log_file_path[log_name], 'a')

    def _load(self):
        self._add("Creating training data in file", self.name)
        self.training_in_data_file = open(self.training_data_path + "/" + self.training_in_data_file_name, 'a')
        self._add("Creating training data out file", self.name)
        self.training_out_data_file = open(self.training_data_path + "/" + self.training_out_data_file_name, 'a')

    def save_training_data(self, _in, out):
        self._add("Saving training data in", self.name)
        for v in _in:
            self.training_in_data_file.write(str(v) + "\n")
        self._add("Saving training data out", self.name)
        for i in out:
            self.training_out_data_file.write(str(i) + "\n")
        self.training_in_data_file.close()
        self.training_out_data_file.close()
        self.training_in_data_file = open(self.training_data_path + "/" + self.training_in_data_file_name, 'a')
        self.training_out_data_file = open(self.training_data_path + "/" + self.training_out_data_file_name, 'a')

    def save_settings(self, env, agent, network):
        with open(self.env_file_path, 'w') as fp:
            json.dump(env, fp, indent = 4)
        with open(self.agent_file_path, 'w') as fp:
            json.dump(agent, fp, indent = 4)
        with open(self.network_file_path, 'w') as fp:
            json.dump(network, fp, indent = 4)

    def save_logs(self, logs, name):
        self.log_file[name] = open(self.log_file_path[name], 'a')
        self.log_file[name].write(logs)
        self.log_file[name].close()

    def save_conf(self, conf):
        self.conf_file = open(self.conf_file_path, 'w')
        self.conf_file.write(conf)
        self.conf_file.close()

    def _save(self, conf=None, logs=None, logs_name=None):
        if conf:
            self.save_conf(conf)
        if logs:
            self.save_logs(logs, logs_name)

    def _end(self):
        self._add("Closing model configuration file", self.name)
        self.model_conf_file.close()
        self._add("Closing log file", self.name)
        self.log_file.close()
