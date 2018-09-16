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
import json

class Local_env(Environnement):

    def __init__(self, mode="train", gui=0, contract_type="classic", config=None):

        Environnement.__init__(self, gui=0)
        if "cfd" in contract_type:
            self.contracts = CFD()
        elif "classic" in contract_type:
            self.contracts = Classic()
        else:
            raise ValueError("Contract type does not exist")

        self.model_name = "PPO"

        self.crypto = ['BTC', 'LTC', 'BCH', 'ETH']
        self.is_crypto = False

        self.stock_name = "BTC_EUR_2018_09_14"
        self.model_dir = self.model_name + "_" + self.stock_name.split("_")[0]
        self.episode_count = 500
        self.window_size = 20
        self.batch_size = 32

        self.mode = mode

        self.wallet = self.contracts.getWallet()
        self.inventory = self.contracts.getInventory()

        self.settings = dict(
            network = self.get_network(),
            agent = self.get_agent_settings(),
            env = self.get_env_settings()
        )

        self.saver = Saver()

        if self.saver.check_settings_files(config):
            self.settings['env'], self.settings['agent'], self.settings['network'] = self.saver.load_settings(config)
            self.get_settings(self.settings['env'], self.settings['agent'])
        else:
            self.saver.save_settings(self.settings['env'],
                self.settings['agent'], self.settings['network'], config)
        self.saver._check(self.model_dir, self.settings)

        self.data, self.raw, self._date = getStockDataVec(self.stock_name)
        self.state = getState(self.raw, 0, self.window_size + 1)

        if self.stock_name.split("_")[0] in self.crypto:
            self.is_crypto = True

        if self.is_crypto and 'cfd' in contract_type:
            raise ValueError("Cryptocurrencies cannot be traded as cfd.\
                \nPlease change contract type to classic.")

        self.len_data = len(self.data) - 1

        self.logger = Logger()
        self.logger.set_log_path(self.saver.get_model_dir()+"/")
        self.logger.new_logs(self._name)
        self.logger.start()

        self.r_period = 10


        self.check_dates()

    def get_agent_settings(self):
        if self.model_name in self.agents:
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore",category=FutureWarning)
                tmp_agent = getattr(__import__('agents'), self.model_name)
        else:
            raise ValueError('could not import %s' % self.model_name)

        agent = tmp_agent.get_specs(env=self)

        return agent

    def get_env_settings(self):
        self.contract_settings = self.contracts.getSettings()

        self.meta = dict(
            episodes = self.episode_count,
            window_size = self.window_size,
            batch_size = self.batch_size,
            agent = self.model_name,
            stock = self.stock_name,
        )

        self.indicators = dict(
            RSI = 'default',
            MACD = 'default',
            Volatility = 'default',
            EMA = [20, 50, 100],
            Bollinger_bands = 'default',
            Stochastic = None
        )

        env = [self.contract_settings,
               self.wallet.settings,
               self.wallet.risk_managment,
               self.meta]

        return env

    def rewa(self):
        self.r_av.append(self.r_pnl[self.current_step['step']] - self.r_pnl[self.current_step['step'] - 1])
        if self.current_step['step'] > 0:
            if self.current_step['step'] > self.r_period:
                return np.average(self.r_av[self.current_step['step']-self.r_period:])
            else:
                return np.average(self.r_av)
        else:
            return 0

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
        self.contract_settings['contract_price'] = self.contracts.getContractPrice(self.data[self.current_step['step']])
        self.reward['current'] = 0
        self.wallet.profit['current'] = 0
        if self.is_crypto:
            self.contract_settings['contract_size'] = self.wallet.manage_contract_size(self.contract_settings)
        self.price['buy'], self.price['sell'] = self.contracts.calcBidnAsk(self.data[self.current_step['step']])
        self.wallet.manage_exposure(self.contract_settings)
        stopped = self.inventory.stop_loss(self)
        if not stopped:
            force_closing = self.inventory.trade_closing(self)
            if not force_closing:
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
        self.wallet.manage_wallet(self.inventory.get_inventory(), self.price,
                            self.contract_settings)
        self.r_pnl.append(self.wallet.settings['GL_profit'])
        #self.reward['current'] += round(self.rewa(), 4)
        #self.reward['current'] += (self.r_pnl[self.current_step['step']] - self.r_av[self.current_step['step']])
        self.wallet.profit['daily'] += self.wallet.profit['current']
        self.wallet.profit['total'] += self.wallet.profit['current']
        self.reward['daily'] += self.reward['current']
        self.reward['total'] += self.reward['current']
        self.lst_reward.append(self.reward['current'])
        self.def_act()

        if self.gui == 1:
            self.chart_preprocessing(self.data[self.current_step['step']])
        self.state = getState(self.raw, self.current_step['step'] + 1,
                            self.window_size + 1)
        self.wallet.daily_process()
        '''
        tqdm.write("Reward: " + str(self.reward['current']) +
                   " | Profit: " + str(self.wallet.profit['current']) +
                   " | G/L: " + str(self.wallet.settings['GL_profit']) +
                   " | Inventory: " + str(self.inventory.get_inventory()))

        if stopped:
            tqdm.write("closed")
        if force_closing:
            tqdm.write("force closed")
        '''
        done = True if self.len_data - 1 == self.current_step['step'] else False
        if self.wallet.risk_managment['current_max_pos'] < 1: #or \
            #self.wallet.risk_managment['current_max_pos'] <= int(self.wallet.risk_managment['max_pos'] // 2):
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
        self.step_left = 0
        self.lst_reward_daily = []
        self.lst_data_full = deque(maxlen=100)
        self.date['day'] = 1
        self.date['month'] = 1
        self.date['year'] = 1
        self.date['total_minutes'] = 1
        self.date['total_day'] = 1
        self.date['total_month'] = 1
        self.date['total_year'] = 1

        self.r_pnl = []
        self.r_av = []
        self.start = 0
        self.switch = 0

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
        self.state = getState(self.raw, 0, self.window_size + 1)
        self.current_step['episode'] += 1
        self.logger._add("Starting episode : " + str(self.current_step['episode']),
                    self._name)
        return self.state
