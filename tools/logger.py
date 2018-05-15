from .utils import str2bool

import time

from collections import deque

class Logger(object):

    def __init__(self):

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
