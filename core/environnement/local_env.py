from .base.base_env import Environnement
from .contracts import CFD, Classic
from tools import *

import pandas as pd
import numpy as np
from collections import deque
from tqdm import tqdm, trange

import os
import sys
import time

class Local_env(Environnement):

    def __init__(self, mode, gui=0, contract_type="classic"):

        Environnement.__init__(self, gui)

        if "cfd" in contract_type:
            self.contracts = CFD()
        elif "classic" in contract_type:
            self.contracts = Classic()
        else:
            raise ValueError("Contract does not exist")

        self.stock_name = "DAX30_1M_2018_04"
        self.model_dir = self.model_name + "_" + self.stock_name.split("_")[0]
        self.episode_count = 500
        self.window_size = 10
        self.batch_size = 32

        self.mode = mode

        self.wallet = self.contracts.getWallet()
        self.inventory = self.contracts.getInventory()

        self.data, self.raw, self._date = getStockDataVec(self.stock_name)

        self.state = getState(self.raw,
                                0,
                                self.window_size + 1)

        self.len_data = len(self.data) - 1

        self.settings = dict(
            network = self.get_network(),
            agent = self.get_agent_settings(),
            env = self.get_env_settings()
        )

        self.logger = Logger()
        self.logger._load_conf(self)
        self.check_dates()

    def init_logger(self):
        self.logger.init_saver(self)
        self.logger._load()
        self.logger.new_logs(self._name)

    def get_env_settings(self):
        self.contract_settings = dict(
            pip_value = 5,
            contract_price = 125,
            spread = 1,
            allow_short = False
        )

        self.meta = dict(
            window_size = self.window_size,
            batch_size = self.batch_size
        )

        env = [self.contract_settings,
               self.wallet.settings,
               self.wallet.risk_managment,
               self.meta]

        return env

    def execute(self, action):
        if self.pause == 1:
            while (self.pause == 1):
                time.sleep(0.01)
        self.current_step['step'] += 1
        self.closed = False
        self.action = action
        if self.step_left == 0:
            self.check_time_before_closing()
        self.step_left -= 1
        self.price['buy'] = self.data[self.current_step['step']] - (self.contract_settings['spread'] / 2)
        self.price['sell'] = self.data[self.current_step['step']] + (self.contract_settings['spread'] / 2)
        self.reward['current'] = 0
        self.wallet.profit['current'] = 0
        self.wallet.manage_exposure(self.contract_settings)
        stopped = self.inventory.stop_loss(self)
        if stopped == False:
            force_closing = self.inventory.trade_closing(self)
            if force_closing == False:
                self.inventory.inventory_managment(self)
            else:
                if self.inventory.get_last_trade()['close']['pos'] == "SELL":
                    self.action = 2
                else:
                    self.action = 1
        else:
            if self.inventory.get_last_trade()['close']['pos'] == "SELL":
                self.action = 2
            else:
                self.action = 1
        self.train_in.append(self.state)
        self.train_out.append(act_processing(self.action))
        self.wallet.profit['daily'] += self.wallet.profit['current']
        self.wallet.profit['total'] += self.wallet.profit['current']
        self.reward['daily'] += self.reward['current']
        self.reward['total'] += self.reward['current']
        self.lst_reward.append(self.reward['current'])
        self.def_act()
        self.wallet.manage_wallet(self.inventory.get_inventory(), self.price, self.contract_settings)
        if self.gui == 1:
            self.chart_preprocessing(self.data[self.current_step['step']])
        self.state = getState(
                            self.raw,
                            self.current_step['step'] + 1,
                            self.window_size + 1)
        self.wallet.daily_process()
        done = True if self.len_data - 1 == self.current_step['step'] else False
        if self.wallet.risk_managment['current_max_pos'] < 1 or self.wallet.risk_managment['current_max_pos'] <= int(self.wallet.risk_managment['max_pos'] // 2):
            self.wallet.settings['capital'] = self.wallet.settings['saved_capital']
            done = True
        self.daily_processing(done)
        return self.state, done, self.reward['current']

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
        self.daily_reset()
        self.wallet.reset()
        self.inventory.reset()

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

        self.tensorOCHL = [[] for _ in range(4)]
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
        self.current_step['step'] = -1
        self.reward['total'] = 0
        self.new_episode = True
        self.state = getState(self.raw,
                                0,
                                self.window_size + 1)
        self.current_step['episode'] += 1
        self.logger._add("Starting episode : " + str(self.current_step['episode']), self._name)
        return self.state