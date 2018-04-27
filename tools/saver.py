import os
import time

import keras

class Saver:

    def __init__(self):

        self.root_path = "./save/"

        self.log_file_name = ""
        self.model_file_name = ""
        self.conf_file_name = "conf.cfg"
        self.model_conf_file_name = "model_conf.cfg"
        self.model_summary_file_name = ""
        self.training_in_data_file_name = "train_in.txt"
        self.training_out_data_file_name = "train_out.txt"

        self.log_file = None
        self.conf_file = None
        self.model_conf_file = None
        self.model_file = None
        self.model_summary_file = None
        self.training_in_data_file = None
        self.training_out_data_file = None

        self.log_file_path = ""
        self.conf_file_path = "" + self.conf_file_name
        self.model_conf_file_path = ""
        self.model_file_path = ""
        self.model_summary_file_path = ""
        self.training_data_path = "training_data/"

    def check_save_dir(self):
        self._add("Checking save directory")
        if os.path.exists(self.root_path) is False:
            os.mkdir(self.root_path)

    def check_model_dir(self, model_name):
        self._add("Checking model directory")
        self.path = self.root_path + model_name + "/"
        if os.path.exists(self.path) is False:
            os.mkdir(self.path)
        else:
            self.model_file_name = self.check_model_file(model_name)
        if self.model_file_name == "":
            self.model_file_path = self.path
        else:
            self.model_file_path = self.path + self.model_file_name
        self.model_conf_file_path = self.path + self.model_conf_file_name
        self.model_summary_file_path = self.path + model_name.replace(".h5", "") + "_summary.txt"

    def check_log_dir(self, log_path):
        self._add("Checking log directory")
        tmp_path = self.path + log_path
        if os.path.exists(tmp_path) is False:
            os.mkdir(tmp_path)
            self.log_file_name = "logs_" + time.strftime("%Y_%m_%d") + ".txt"
        else:
            self.log_file_name = self.check_log_file()
        self.log_file_path = tmp_path + "/" + self.log_file_name

    def check_training_data_dir(self):
        tmp_path = self.path + self.training_data_path
        if os.path.exists(tmp_path) is False:
            os.mkdir(tmp_path)
        self.training_data_path = tmp_path

    def check_model_file(self, model_name):
        self._add("Checking model files")
        cdir = os.listdir(self.path)
        for d in cdir:
            if model_name in d:
                return d
        return ""

    def check_log_file(self):
        self._add("Checking logs files")
        cdir = os.listdir(self.path)
        for d in cdir:
            if "logs_" in d and time.strftime("%Y_%m_%d") in d:
                return d
        return "logs_" + time.strftime("%Y_%m_%d") + ".txt"

    def _check(self, model_name, log_path):
        self.check_save_dir()
        self.check_model_dir(model_name)
        self.check_log_dir(log_path)
        self.check_training_data_dir()

    def load_model_summary(self):
        self.model_summary_file = open(self.model_summary_file_path, 'r')

    def load_conf(self):
        if not os.path.exists(self.conf_file_path):
            #self._add("Creating configuration file")
            open(self.conf_file_path, 'a').close()
        #self._add("Loading configuration file")
        self.conf_file = open(self.conf_file_path, 'r')

    def _load(self):
        self._add("Loading logs file")
        self.log_file = open(self.log_file_path, 'a')

        self._add("Creating model configuration file")
        open(self.model_conf_file_path, 'a').close()
        self.training_in_data_file = open(self.training_data_path + "/" + self.training_in_data_file_name, 'a')
        self.training_out_data_file = open(self.training_data_path + "/" + self.training_out_data_file_name, 'a')
        if os.path.exists(self.model_summary_file_path) is False:
            self.model_summary_file = open(self.model_summary_file_path, 'w')

    def save_training_data(self, _in, out):
        self.training_in_data_file.write(str(_in))
        self.training_out_data_file.write(str(out))
        self.training_in_data_file.close()
        self.training_out_data_file.close()
        self.training_in_data_file = open(self.training_data_path + "/" + self.training_in_data_file_name, 'a')
        self.training_out_data_file = open(self.training_data_path + "/" + self.training_out_data_file_name, 'a')

    def save_model_summary(self, model):
        model.summary(print_fn=lambda x: self.model_summary_file.write(x + "\n"))
        self.model_summary_file.close()

    def save_logs(self, logs):
        self.log_file.write(logs)
        self.log_file.close()
        self.log_file = open(self.log_file_path, 'a')

    def save_conf(self, conf):
        self.conf_file = open(self.conf_file_path, 'w')
        self.conf_file.write(conf)
        self.conf_file.close()

    def save_model_conf(self, conf):
        self.model_conf_file = open(self.model_conf_file_path, 'w')
        self.model_conf_file.write(conf)
        self.model_conf_file.close()

    def _save(self, conf=None, logs=None, model_conf=None):
        if conf:
            self.save_conf(conf)
        if model_conf:
            self.save_model_conf(model_conf)
        if logs:
            self.save_logs(logs)

    def _end(self):
        self._add("Closing model configuration file")
        self.model_conf_file.close()
        self._add("Closing log file")
        self.log_file.close()
