from PyQt5.QtCore import *

from .worker import Worker
from environnement import Environnement
from tools import *

import time

import pandas as pd

from tqdm import tqdm

class Local_Worker(Worker):

    def __init__(self, env):
        self.env = env
        if self.env.gui == 0:
            self.env.init_logger()
        Worker.__init__(self, env)

    def run(self):
        self.init_agent()

        for e in tqdm(range(self.env.episode_count + 1)):
            self.env.cepisode = e + 1
            self.env.start_t = time.time()

            # Init agent inventory
            self.agent.inventory = pd.DataFrame(columns = self.columns)

            if self.env.pause == 1:
                while (self.env.pause == 1):
                    time.sleep(0.01)

            state = getState(self.raw,
                             0,
                             self.env.window_size + 1)

            for t in tqdm(range(self.env.data)):
                if self.env.pause == 1:
                    while (self.env.pause == 1):
                        time.sleep(0.01)
                b = 0
                tmp = time.time()
                self.env.cdatai = t
                self.env.cdata = self.data[t]
                self.env.lst_data.append(self.env.cdata)
                self.env.POS_SELL = -1
                self.env.POS_BUY = -1

                done = True if t == self.env.data - 1 else False

                # Get action from agent
                self.action = self.agent.act(state)
                self.env.def_act(self.action)

                # Get new state
                next_state = getState(self.raw,
                                      t + 1,
                                      self.env.window_size + 1)
                self.env.lst_state.append(self.env.cdata)

                # Update buy price with spread
                self.env.buy_price = self.data[t] - (self.env.spread / 2)
                # Update sell price with spread
                self.env.sell_price = self.data[t] + (self.env.spread / 2)

                self.env.reward = 0 # Reset reward
                self.env.profit = 0 # Reset current profit

                self.env.manage_exposure()

                if self.pip_drawdown_checking() == 0:
                    self.inventory_managment()

                self.env.inventory = self.agent.inventory
                self.env.daily_profit += self.env.profit
                self.env.train_in.append(state)
                self.env.train_out.append(act_processing(self.env.lst_act[len(self.env.lst_act) - 1]))

                if self.env.manage_date() == 1:
                    #self.env.reward += ((self.env.daily_win - self.env.daily_loose) * 10)
                    if self.env.daily_profit > 0:
                        self.env.logger.save_training_data(self.env.train_in,
                                                           self.env.train_out)
                    self.daily_profit = 0
                    self.env.train_in = []
                    self.env.train_out = []
                    self.env.daily_win = 0
                    self.env.daily_loose = 0

                self.env.manage_wallet()

                if self.env.cmax_pos < 1 or self.env.cmax_pos <= int(self.env.max_pos // 2):
                    self.env.capital = self.env.scapital
                    #self.env.reward -= 1000

                self.update_env() # Updating env from agent for GUI
                self.env.chart_preprocessing(self.data[t])
                self.sig_step.emit() # Update GUI
                self.agent.memory.append((state,
                                          self.action,
                                          self.env.reward,
                                          next_state,
                                          done))
                state = next_state

                if "train" in self.env.mode:
                    if len(self.agent.memory) > self.env.batch_size:
                        self.env.lst_loss.append(self.agent.expReplay(self.env.batch_size))
                        self.sig_batch.emit()
                    if t % 1000 == 0 and t > 0 : # Save model all 1000 step
                        self.agent._save_model()
                        if "DDQN" == self.env.model_name or "DDRQN" == self.env.model_name or "DDPG" == self.env.model_name:
                            self.agent.update_target_model()
                else:
                    time.sleep(0.01)
                self.env.loop_t = time.time() - tmp


            self.env.manage_h_lst()
            self.sig_episode.emit()
