from tools import *

import time
import sys

from tqdm import tqdm
tqdm.monitor_interval = 0

from PyQt5.QtCore import *

class Live_Worker(QThread):

    sig_step = pyqtSignal()
    sig_batch = pyqtSignal()
    sig_episode = pyqtSignal()

    def __init__(self, env=None, agent=None):
        self.name = os.path.basename(__file__).replace(".py", "")

        if env == None or agent == None:
            raise ValueError("The worker need an agent and an environnement")

        if env.gui == 0:
            env.init_logger()
            env.logger._save_conf(env)

        self.env = env
        self.agent = agent
        #env.logger.new_logs(self.name)
        #env.logger._add("Initialization", self.name)
        QThread.__init__(self)

    def run(self):
        if self.env.gui == 0:
            ep = tqdm(range(self.env.episode_count), desc="Episode processing ")
        else:
            ep = range(self.env.episode_count)

        try:
            # Should define an 'episode' for Live_Worker
            for e in ep:
                state = self.env.reset()
                self.agent.reset()
                self.env.start_t = time.time()
                dat = range(self.env.len_data)
                if self.env.gui == 0:
                    dat = tqdm(dat, desc="Step Processing ")
                for t in dat:
                    tmp = time.time()
                    action = self.agent.act(state) # Get action from agent
                    # Get new state
                    next_state, terminal, reward = self.env.execute(action)
                    self.sig_step.emit() # Update GUI
                    state = next_state
                    if "train" in self.env.mode:
                        self.agent.observe(reward=reward, terminal=terminal)
                        if t % (self.env.len_data // 10) == 0 and t > 0 :
                            self.agent._save_model()
                    if self.env.gui == 1:
                        time.sleep(0.07)
                    elif self.env.gui == 0:
                        dat.update(1)
                    self.env.loop_t = time.time() - tmp
                    if terminal is True or self.agent.should_stop():
                        break

                if self.env.gui == 0:
                    dat.close()
                self.env.episode_process()
                self.sig_episode.emit()
                if self.agent.should_stop():
                    break

        except KeyboardInterrupt:
            sys.exit(0)
