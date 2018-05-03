from tools import Logger
from tools import *
from .inventory import Inventory
from .wallet import Wallet

import pandas as pd
import numpy as np
from collections import deque
from tqdm import tqdm

import os
import sys
import time

class Environnement:

    def __init__(self, gui):

        # Software settings

        self._name = os.path.basename(__file__).replace(".py", "")
        self.name = "TradzQAI"
        self.version = "v0.2"
        self.v_state = "Alpha"
        self._platform = sys.platform
        self.agents = self.src_agents()
        self.gui = gui

        # Agent settings

        self.model = None
        self.model_name = "TRPO"
        self.mode = ""

        ## Hyperparameters

        self.hyperparameters = dict(
            update_rate = 1e-1,
            learning_rate = 1e-3,
            gamma = 0.95,
            epsilon = 1.0,
            epsilon_min = 1e-2,
            epsilon_decay = 0.995
        )

        # Environnement settings

        self.stock_name = "DAX30_1M_2017_11"
        self.model_dir = self.model_name + "_" + self.stock_name.split("_")[0]
        self.episode_count = 500
        self.window_size = 30
        self.batch_size = 64

        # Contract settings

        self.contract_settings = dict(
            pip_value = 5,
            contract_price = 125,
            spread = 1,
            allow_short = False
        )

        # Risk managment

        # Wallet settings
        self.daily_trade = dict(
            win = 0,
            loss = 0,
            draw = 0,
            total = 0
        )

        self.reward = dict(
            current = 0,
            daily = 0,
            total = 0
        )

        self.current_step = dict(
            order = "",
            episode = 0,
            step = 0
        )

        self.trade = dict(
            win = 0,
            loss = 0,
            draw = 0,
            total = 0,
        )

        self.date = dict(
            day = 1,
            month = 1,
            year = 1,
            total_minutes = 1,
            total_day = 1,
            total_month = 1,
            total_year = 1
        )
        # Wallet state
        self.step_left = 0


        self.max_return = 0
        self.max_drawdown = 0

        # Agent state

        self.pause = 0

        self.action = None

        # Worker env helper

        self.price = dict(
            buy = 0,
            sell = 0
        )

        self.data = None
        self.POS_BUY = -1
        self.POS_SELL = -1

        # Current data and order dropped from inventory

        self.last_closed_order = dict(
            current_price = 0,
            current_pos = ""
        )

        # Current data and order from loop


        # Time

        self.start_t = 0
        self.loop_t = 0

        # date

        self._date = None

        # Other

        self.mod_ordr = False
        self.day_changed = False
        self.new_episode = False

        # List for graph building

        ## Daily list

        ### Overview list

        self.lst_data = []
        self.lst_inventory_len = []
        self.lst_return = deque(maxlen=1000)
        self.lst_mean_return = []
        self.lst_sharp_ratio = []
        self.lst_drawdown = []
        self.lst_win_order = []
        self.lst_loose_order = []
        self.lst_draw_order = []
        self.lst_capital = []

        ### Model list

        self.lst_act = deque(maxlen=1000)
        self.lst_reward = deque(maxlen=1000)
        self.lst_state = deque(maxlen=1000)

        # Training datasets

        self.train_in = []
        self.train_out = []

        # Gui helper

        self.time = None
        self.lst_data_full = deque(maxlen=100)
        self.lst_data_preprocessed = []
        self.offset = 0

        self.lst_reward_daily = []

        # Managment

        self.logger = None
        self.readed = None



        self.wallet = Wallet()
        self.inventory = Inventory(self.wallet.risk_managment['stop_loss'])
        #self.reset()
        self._load_conf()
        self.data, self.raw, self._date = getStockDataVec(self.stock_name)
        self.check_dates()

    def _pause(self):
        self.pause = 1

    def _resume(self):
        self.pause = 0

    def init_logger(self):
        self.logger.init_saver(self)
        self.logger._load()
        #self.logger.new_logs(self._name)

    def def_act(self):
        if self.action == 1:
            self.act = "BUY"
            self.lst_act.append(1)
        elif self.action == 2:
            self.act = "SELL"
            self.lst_act.append(-1)
        else:
            self.act = "HOLD"
            self.lst_act.append(0)

    def manage_orders(self, ordr):
        if self.POS_BUY > -1 or self.POS_SELL > -1:
            last_trade = self.inventory.get_last_trade()
            new = [str(last_trade['open']['pos']) \
                   + " : " \
                   + '{:.2f}'.format(last_trade['open']['price']) \
                   + " -> " \
                   + str(last_trade['close']['pos']) \
                   + " : " \
                   + '{:.2f}'.format(last_trade['close']['price']) \
                   + " | Profit : " \
                   + '{:.2f}'.format(self.wallet.profit['current'])]

            if len(ordr['Orders']) > 37:
                ordr = (ordr.drop(0)).reset_index(drop=True)
            tmp = pd.DataFrame(new, columns = ['Orders'])
            ordr = ordr.append(tmp, ignore_index=True)
            self.mod_ordr = True
        else:
            self.mod_ordr = False
        return ordr

    def src_agents(self):
        ignore = ['agent.py', '__init__.py', '__pycache__']
        valid = []
        for f in os.listdir("agents"):
            if f not in ignore:
                valid.append(f.replace(".py", ""))
        return valid

    def check_dates(self):
        self._date = self._date.apply(lambda x: x.replace(" ", "")[:12])
        if self.gui == 0:
            ldate = tqdm(range(1, len(self._date) - 1), desc = "Checking dates ")
        else:
            ldate = range(1, len(self._date) - 1)
        for r in ldate:
            date_c = self._date[r]
            date_p = self._date[r - 1]
            if date_p[11] != date_c[11]:
                self.date['total_minutes'] += 1
            if date_p[7] != date_c[7]:
                self.date['total_day'] += 1
            if date_p[5] != date_c[5]:
                self.date['total_month'] += 1
            if date_p[3] != date_c[3]:
                self.date['total_day'] += 1
        if self.date['total_minutes'] != len(self._date) - 1:
            self.time = "Tick"
        else:
            self.time = "1M"

    def check_time_before_closing(self):
        for idx in range(self.current_step['step'] + 1 , len(self._date) - 1):
            if self._date[idx - 1][7] != self._date[idx][7]:
                break
        self.step_left = idx - self.current_step['step'] + 1


    def manage_date(self):
        self.day_changed = False
        if self.current_step['step'] > 0:
            if self._date[self.current_step['step'] - 1][3] != self._date[self.current_step['step']][3]:
                self.date['year'] += 1
                self.date['month'] = 1
                self.date['day'] = 1
                self.day_changed = True
            elif self._date[self.current_step['step'] - 1][5] != self._date[self.current_step['step']][5]:
                self.date['month'] += 1
                self.date['day'] = 1
                self.day_changed = True
            elif self._date[self.current_step['step'] - 1][7] != self._date[self.current_step['step']][7]:
                self.date['day'] += 1
                self.day_changed = True
        if self.day_changed is True:
            return 1
        else:
            return 0

    def chart_preprocessing(self, data):
        if self.current_step['step'] == 0:
            self.lst_data_preprocessed = [data, data, data, data]
            self.lst_data_full.append((0,
                                       self.lst_data_preprocessed[0], #open
                                       self.lst_data_preprocessed[1], #close
                                       self.lst_data_preprocessed[2], #min
                                       self.lst_data_preprocessed[3], #high
                                       self.lst_act[len(self.lst_act) - 1]))

        #toutes les 5 ou 1 M ajouter nouvelle entrer dans la liste
        #modifier la liste dans cet interval
        if self.time == "Tick":
            #Passage en 1M
            if self.current_step['step'] > 0 and self._date[self.current_step['step'] - 1][11] != self._date[self.current_step['step']][11]:
                self.lst_data_preprocessed = [data, data, data, data]
                self.lst_data_full.append((int(self.current_step['step'] - self.offset),
                                           self.lst_data_preprocessed[0], #open
                                           self.lst_data_preprocessed[1], #close
                                           self.lst_data_preprocessed[2], #min
                                           self.lst_data_preprocessed[3], #high
                                           self.lst_act[len(self.lst_act) - 1]))
            else:
                if self.current_step['step'] > 0:
                    self.offset += 1
                if self.lst_data_preprocessed[2] > data:
                    self.lst_data_preprocessed[2] = data
                if self.lst_data_preprocessed[3] < data:
                    self.lst_data_preprocessed[3] = data
                self.lst_data_preprocessed[1] = data
                self.lst_data_full[len(self.lst_data_full) - 1] = (int(self.current_step['step'] - self.offset),
                                           self.lst_data_preprocessed[0], #open
                                           self.lst_data_preprocessed[1], #close
                                           self.lst_data_preprocessed[2], #min
                                           self.lst_data_preprocessed[3], #high
                                           self.lst_act[len(self.lst_act) - 1])
        elif self.time == "1M":
            #Passage en 5M
            if self._date[self.current_step['step']][11] == "0" or self._date[self.current_step['step']][11] == "5":
                self.lst_data_preprocessed = [data, data, data, data]
                self.lst_data_full.append((int(self.current_step['step'] - self.offset),
                                           self.lst_data_preprocessed[0], #open
                                           self.lst_data_preprocessed[1], #close
                                           self.lst_data_preprocessed[2], #min
                                           self.lst_data_preprocessed[3], #high
                                           self.lst_act[len(self.lst_act) - 1]))
            else:
                if self.current_step['step'] > 0:
                    self.offset += 1
                if self.lst_data_preprocessed[2] > data:
                    self.lst_data_preprocessed[2] = data
                if self.lst_data_preprocessed[3] < data:
                    self.lst_data_preprocessed[3] = data
                self.lst_data_preprocessed[1] = data
                self.lst_data_full[len(self.lst_data_full) - 1] = (int(self.current_step['step'] - self.offset),
                                           self.lst_data_preprocessed[0], #open
                                           self.lst_data_preprocessed[1], #close
                                           self.lst_data_preprocessed[2], #min
                                           self.lst_data_preprocessed[3], #high
                                           self.lst_act[len(self.lst_act) - 1])

    def _load_conf(self):
        self.logger = Logger()
        self.logger.load_conf()
        try:
            lines = self.logger.conf_file.read()
            lines = lines.split("\n")
        except:
            lines = ""
        self.readed = lines
        for line in lines:
            if "Model name" in line:
                self.model_name = (line.split(":")[1]).replace(" ", "")
            if "Learning rate" in line:
                self.hyperparameters['learning_rate'] = float((line.split(":")[1]).replace(" ", ""))
            if "Gamma" in line:
                self.hyperparameters['gamma'] = float((line.split(":")[1]).replace(" ", ""))
            if "Espilon" in line:
                self.hyperparameters['epsilon'] = float((line.split(":")[1]).replace(" ", ""))
            if "Stock name" in line:
                self.stock_name = (line.split(":")[1]).replace(" ", "")
            if "Window size" in line:
                self.window_size = int((line.split(":")[1]).replace(" ", ""))
            if "Episode" in line:
                self.episode_count = int((line.split(":")[1]).replace(" ", ""))
            if "Batch size" in line:
                self.batch_size = int((line.split(":")[1]).replace(" ", ""))
            if "Contract price" in line:
                self.contract_settings['contract_price'] = int((line.split(":")[1]).replace(" ", ""))
            if "Pip value" in line:
                self.contract_settings['pip_value'] = int((line.split(":")[1]).replace(" ", ""))
            if "Spread" in line:
                self.contract_settings['spread'] = float((line.split(":")[1]).replace(" ", ""))
            if "Capital" in line:
                self.wallet.settings['capital'] = int((line.split(":")[1]).replace(" ", ""))
                self.wallet.settings['saved_capital'] = self.wallet.settings['capital']
                self.wallet.settings['usable_margin'] = self.wallet.settings['capital']
            if "Exposure" in line:
                self.wallet.risk_managment['exposure'] = float((line.split(":")[1]).replace(" ", ""))
            if "Max pip loss" in line:
                self.wallet.risk_managment['stop_loss'] = int((line.split(":")[1]).replace(" ", ""))
            if "Max pos" in line:
                self.wallet.risk_managment['max_pos'] = int((line.split(":")[1]).replace(" ", ""))
        self.model_dir = self.model_name + "_" + self.stock_name.split("_")[0]
        self.logger.conf_file.close()

    def execute(self, action):
        self.action = action
        self.POS_BUY = -1
        self.POS_SELL = -1
        done = True if len(self.data) == self.current_step['step'] - 1 else False
        if self.step_left == 0:
            self.check_time_before_closing()
        self.step_left -= 1
        self.price['buy'] = self.data[self.current_step['step']] - (self.contract_settings['spread'] / 2)
        self.price['sell'] = self.data[self.current_step['step']] + (self.contract_settings['spread'] / 2)
        self.lst_state.append(self.state[0])
        self.reward['current'] = 0
        self.wallet.profit['current'] = 0
        self.wallet.manage_exposure(self.contract_settings)
        stopped = self.inventory.stop_loss(self)
        if stopped == False:
            force_closing = self.inventory.trade_closing(self)
            if force_closing == False:
                self.inventory.inventory_managment(self)
            else:
                self.POS_SELL = 0
                if self.inventory.get_last_trade()['close']['pos'] == "SELL":
                    self.action = 2
                else:
                    self.action = 1
        else:
            if self.action == 1:
                self.POS_BUY = 0
                self.action = 2
            elif self.action == 2:
                self.POS_SELL = 0
                self.action = 1
        self.train_in.append(self.state)
        self.train_out.append(act_processing(self.action))
        self.wallet.profit['daily'] += self.wallet.profit['current']
        self.wallet.profit['total'] += self.wallet.profit['current']
        self.reward['daily'] += self.reward['current']
        self.reward['total'] += self.reward['current']
        self.lst_reward.append(self.reward['current'])
        self.lst_return.append(self.wallet.profit['current'])
        self.def_act()
        self.wallet.manage_wallet(self.inventory.get_inventory(), self.price, self.contract_settings)
        self.chart_preprocessing(self.data[self.current_step['step']])
        if self.wallet.risk_managment['current_max_pos'] < 1 or self.wallet.risk_managment['current_max_pos'] <= int(self.wallet.risk_managment['max_pos'] // 2):
            self.wallet.settings['capital'] = self.wallet.settings['saved_capital']
        self.state = getState(self.raw,
                              self.current_step['step'] + 1,
                              self.window_size + 1)
        self.current_step['step'] += 1
        return self.state, done, self.reward['current']

    def avg_reward(self, reward, n):
        if n == 0:
            return np.average(np.array(reward))
        return np.average(np.array(reward[(len(reward) - 1) - n:]))

    def daily_reset(self):
        self.wallet.daily_reset()
        self.lst_reward = []

        self.daily_trade['win'] = 0
        self.daily_trade['loss'] = 0
        self.daily_trade['draw'] = 0
        self.daily_trade['total'] = 0
        self.price['buy'] = 0
        self.price['sell'] = 0
        self.reward['current'] = 0
        self.reward['daily'] = 0

        self.train_in = []
        self.train_out = []

    def reset(self):
        try:
            self.h_lst_reward.append(self.reward['total'])
            self.h_lst_profit.append(self.wallet.profit['total'])
            self.h_lst_win_order.append(self.trade['win'])
            self.h_lst_loose_order.append(self.trade['loss'])
            self.h_lst_draw_order.append(self.trade['draw'])
        except:
            self.h_lst_reward = []
            self.h_lst_profit = []
            self.h_lst_win_order = []
            self.h_lst_loose_order = []
            self.h_lst_draw_order = []

        self.lst_reward_daily = []
        self.lst_data_full = deque(maxlen=100)
        self.date['day'] = 1
        self.date['month'] = 1
        self.date['year'] = 1
        self.date['total_minutes'] = 1
        self.date['total_day'] = 1
        self.date['total_month'] = 1
        self.date['total_year'] = 1
        self.trade['win'] = 0
        self.trade['loss'] = 0
        self.trade['draw'] = 0
        self.trade['total'] = 0
        self.current_step['order'] = ""
        self.current_step['episode'] = 0
        self.current_step['step'] = 0
        self.daily_reset()
        self.wallet.reset()
        self.inventory.reset()
        self.reward['total'] = 0
        self.new_episode = True
        self.state = getState(self.raw,
                              0,
                              self.window_size + 1)
        self.current_step['episode'] += 1
        return self.state
