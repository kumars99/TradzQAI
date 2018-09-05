from tools import *

import time
import sys
import numpy as np

from tqdm import tqdm
tqdm.monitor_interval = 0

from PyQt5.QtCore import *

class Local_Worker(QThread):

    sig_step = pyqtSignal()
    sig_batch = pyqtSignal()
    sig_episode = pyqtSignal()

    def __init__(self, env=None, agent=None):
        self.name = os.path.basename(__file__).replace(".py", "")

        if not env or not agent:
            raise ValueError("The worker need an agent and an environnement")

        self.env = env
        self.agent = agent
        #env.logger.new_logs(self.name)
        #env.logger._add("Initialization", self.name)
        if "eval" in self.env.mode:
            self.env.episode_count = 1
        QThread.__init__(self)


    def run(self):
        ep = range(self.env.episode_count)
        if self.env.gui == 0:
            ep = tqdm(ep, desc="Episode processing ")

        for e in ep:
            state = self.env.reset()
            #self.agent.reset()
            self.env.start_t = time.time()
            dat = range(self.env.len_data)
            if self.env.gui == 0:
                dat = tqdm(dat, desc="Step Processing ")
            for t in dat:
                tmp = time.time()
                action = self.agent.act(state) # Get action from agent
                # Get new state
                next_state, terminal, reward = self.env.execute(action)
                state = next_state
                if "train" in self.env.mode:
                    self.agent.observe(reward=reward, terminal=terminal)
                if self.env.gui == 1:
                    self.sig_step.emit() # Update GUI
                    time.sleep(0.07)
                elif self.env.gui == 0:
                    dat.update(1)
                self.env.loop_t = time.time() - tmp
                if terminal is True or self.agent.should_stop() or self.env.stop:
                    self.agent.save_model(directory=self.env.saver.model_file_path, append_timestep=True)
                    break

            tqdm.write(str(terminal))
            if self.env.gui == 0:
                dat.close()
            elif self.env.gui == 1:
                self.sig_episode.emit()
            if self.agent.should_stop() or self.env.stop or e == self.env.episode_count - 1:
                break
