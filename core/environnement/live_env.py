from .base import Environnement
from .contracts import CFD, Classic
from tools import *

import pandas as pd
import numpy as np
from collections import deque
from tqdm import tqdm

import os
import sys
import time

class Live_env(Environnement):

    def __init__(self, mode, gui, contract_type):
        Environnement.__init__(self, gui)
        if "cfd" in contract_type:
            self.contracts = CFD()
        elif "classic" in contract_type:
            self.contracts = Classic()
        else:
            raise ValueError("Contract does not exist")

        self.model_name = "PPO"

        self.stock_name = 'BTC-EUR'
        self.model_dir = self.model_name + "_" + self.stock_name.split("_")[0]
        self.episode_count = 500
        self.window_size = 10
        self.batch_size = 32

        self.mode = mode
        self.step_left = 100000

        self.wallet = self.contracts.getWallet()
        self.inventory = self.contracts.getInventory()

        #self.data, self.raw, self._date = getStockDataVec(self.stock_name)
        self.data = [3000.00]
        self._date = []
        self.state = getState(self.data, 0, self.window_size + 1)
        #self.len_data = len(self.data) - 1

        self.settings = dict(
            network = self.get_network(),
            agent = self.get_agent_settings(),
            env = self.get_env_settings()
        )

        self.logger = Logger()
        self.logger._load_conf(self)
        #self.check_dates()

    def init_logger(self):
        self.logger.init_saver(self)
        self.logger._load()
        self.logger.new_logs(self._name)

    def addData(self, data):
        price = float(data['price'])
        date = (data['time'].replace("-", "").replace("T", "").replace("Z",
            "").replace(":", "").replace(".", ""))[:15]
        self.contract_settings['spread'] = float(data['best_bid']) - float(data['best_ask'])
        self.data.append(price)
        self._date.append(date)

    def get_env_settings(self):
        self.contract_settings = self.contracts.getSettings()

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
        self.contract_settings['contract_price'] = self.contracts.getContractPrice(self.data[self.current_step['step']])
        self.closed = False
        self.action = action
        self.price['buy'], self.price['sell'] = self.contracts.calcBidnAsk(self.data[self.current_step['step']])
        self.reward['current'] = 0
        self.wallet.profit['current'] = 0
        self.wallet.manage_exposure(self.contract_settings)
        stopped = self.inventory.stop_loss(self)
        if not stopped:
            self.inventory.inventory_managment(self)
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
        self.wallet.manage_wallet(self.inventory.get_inventory(), self.price,
                self.contract_settings)
        if self.gui == 1:
            self.chart_preprocessing(self.data[self.current_step['step']])
        self.state = getState(self.data, self.current_step['step'], self.window_size + 1)
        self.wallet.daily_process()
        done = True if (int(time.time() - self.start_t) / 60) >= 60 else False
        if self.wallet.risk_managment['current_max_pos'] < 1 or self.wallet.risk_managment['current_max_pos'] <= int(self.wallet.risk_managment['max_pos'] // 2):
            self.wallet.settings['capital'] = self.wallet.settings['saved_capital']
            done = True
        self.daily_processing(done)
        if done:
            self.episode_process()
        return self.state, done, self.reward['current']

    def daily_reset(self):
        self.wallet.daily_reset()
        self.lst_reward = []

        self.daily_trade = dict(
            win = 0,
            loss = 0,
            draw = 0,
            total = 0
        )

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

        self.reward = dict(
            current = 0,
            daily = 0,
            total = 0
        )

        self.trade = dict(
            win = 0,
            loss = 0,
            draw = 0,
            total = 0,
        )

        self.price = dict(
            buy = 0,
            sell = 0
        )

        self.daily_reset()
        self.wallet.reset()
        self.inventory.reset()
        self.current_step['step'] = -1
        self.new_episode = True
        self.state = getState(self.data, 0, self.window_size + 1)
        self.current_step['episode'] += 1
        self.logger._add("Starting episode : " + str(self.current_step['episode']), self._name)
        return self.state
