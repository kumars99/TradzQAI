from tools import Logger

import pandas as pd
import numpy as np
from collections import deque

from PyQt5.QtCore import *

class Environnement:

    def __init__(self):

        # Soft settings

        self.name = "TradzQAI"
        self.version = "v0.2"
        self.v_state = "Alpha"

        # Agent settings

        self.model = None
        self.model_name = "DQN"
        self.mode = ""

        ## Hyperparameters

        self.update_rate = 1e-1
        self.learning_rate = 1e-3
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 1e-2
        self.epsilon_decay = 0.995

        # Environnement settings

        self.stock_name = "DAX30_1M_2017_11"
        self.model_dir = self.model_name + "_" + self.stock_name.split("_")[0]
        self.episode_count = 100
        self.window_size = 20
        self.batch_size = 32

        # Contract settings

        self.spread = 1
        self.pip_value = 5
        self.contract_price = 125

        # Risk managment

        self.max_pos = 10
        self.max_order_size = 1
        self.cmax_pos = self.max_pos
        self.exposure = 10 # Exposure in percent
        self.max_pip_drawdown = 20

        # Wallet settings

        self.capital = 20000

        # Wallet state

        self.scapital = self.capital
        self.cgl = 0
        self.usable_margin = self.capital
        self.used_margin = 0
        self.pip_gl = 0
        self.max_return = 0
        self.max_drawdown = 0

        # Agent state

        self.total_profit = 0
        self.reward = 0
        self.tot_reward = 0
        self.profit = 0
        self.pause = 0
        self.inventory = None
        self.act = ""

        # DQN env helper

        self.data = None
        self.buy_price = 0
        self.sell_price = 0
        self.POS_BUY = -1
        self.POS_SELL = -1

        # Current data and order dropped from inventory

        self.cd = 0
        self.co = ""

        # Current data and order from loop

        self.corder = ""
        self.cdata = 0
        self.cdatai = 0
        self.cepisode = 0

        # Orders

        self.win = 0
        self.loose = 0
        self.draw = 0

        self.daily_win = 0
        self.daily_loose = 0

        # Time

        self.start_t = 0
        self.loop_t = 0

        # date

        self.day = 1
        self.tot_day = 1

        self.month = 1
        self.tot_month = 1

        self.year = 1
        self.tot_year = 1

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
        self.lst_act_predit = []
        self.lst_traget_predict = []
        self.lst_target = []
        self.lst_loss = []
        self.lst_state = deque(maxlen=1000)
        self.lst_epsilon = []

        ## Episode list

        ### Historical list

        self.h_lst_loss = []
        self.h_lst_reward = []
        self.h_lst_profit = []
        self.h_lst_win_order = []
        self.h_lst_loose_order = []
        self.h_lst_draw_order = []
        self.h_lst_capital = []

        self.init_logger()

    # TODO : conf file managment
    #        logs managment

    def init_logger(self):
        self.logger = Logger(self)
        self.logger.init_saver()

    def manage_h_lst(self):
        self.h_lst_loss.append(np.average(self.lst_loss))
        self.h_lst_reward.append(self.tot_reward)
        self.h_lst_profit.append(self.total_profit)
        self.h_lst_win_order.append(self.win)
        self.h_lst_loose_order.append(self.loose)
        self.h_lst_draw_order.append(self.draw)

        self.lst_loss = []
        self.total_profit = 0
        self.tot_reward = 0
        self.win = 0
        self.loose = 0
        self.draw = 0
        self.day = 1
        self.month = 1
        self.year = 1

        self.new_episode = True

    def manage_ov_lst(self):
        self.lst_capital.append(self.capital)
        if self.profit != 0:
            self.lst_return.append(self.profit)
        self.lst_win_order.append(self.win)
        self.lst_loose_order.append(self.loose)
        self.lst_draw_order.append(self.draw)
        self.lst_mean_return.append(np.sum(self.lst_return) / (self.win + self.loose))
        self.lst_sharp_ratio.append(self.lst_mean_return[len(self.lst_mean_return)] / np.std(self.lst_return, ddof=1))

    def def_act(self, act):
        if act == 1:
            self.act = "BUY"
            self.lst_act.append(1)
        elif act == 2:
            self.act = "SELL"
            self.lst_act.append(-1)
        else:
            self.act = "HOLD"
            self.lst_act.append(0)

    def _pause(self):
        self.pause = 1

    def _resume(self):
        self.pause = 0

    def manage_orders(self, ordr):
        if self.POS_BUY > -1 or self.POS_SELL > -1:
            if "SELL" in self.corder:
                POS = self.POS_BUY
                c = self.sell_price
            elif "BUY" in self.corder:
                POS = self.POS_SELL
                c = self.buy_price
            new = [str(self.co) + " : " + '{:.2f}'.format(self.cd) + " -> " + str(self.corder) + " : " + '{:.2f}'.format(c) + " | Profit : " + '{:.2f}'.format(self.profit)]
            if len(ordr['Orders']) > 37:
                ordr = (ordr.drop(0)).reset_index(drop=True)
            tmp = pd.DataFrame(new, columns = ['Orders'])
            ordr = ordr.append(tmp, ignore_index=True)
            self.mod_ordr = True
        else:
            self.mod_ordr = False
        return ordr

    def manage_wallet(self):
        avg = 0
        i = 0
        while i != len(self.inventory['POS']):
            avg += self.inventory['Price'][i]
            i += 1

        if i > 0:
            avg /= i
            if "SELL" in self.inventory['POS'][0]:
                self.cgl = (avg - self.sell_price) * i * self.pip_value * self.max_order_size
            elif "BUY" in self.inventory['POS'][0]:
                self.cgl = (self.buy_price - avg) * i * self.pip_value * self.max_order_size
        else:
            self.cgl = 0

        self.capital += self.profit
        self.used_margin = (len(self.inventory['POS']) * self.contract_price * self.max_order_size) + (self.cgl * -1)
        self.usable_margin = self.capital_exposure - self.used_margin
        if self.used_margin < 0:
            self.used_margin = 0

    def manage_exposure(self):
        self.capital_exposure = self.capital - (self.capital * (1 - (self.exposure / 100)))
        max_order_valid = self.capital_exposure // (self.contract_price + (self.max_pip_drawdown * self.pip_value))
        if max_order_valid <= self.max_pos:
            self.cmax_pos = max_order_valid
            self.max_order_size = 1
        else:
            self.cmax_pos = self.max_pos
            extra_order = max_order_valid - self.max_pos
            if extra_order >= self.max_pos:
                self.max_order_size = int(max_order_valid // self.max_pos)
            else:
                self.max_order_size = 1

    def check_dates(self):
        for r in range(len(self.date)):
            self.date[r] = (self.date[r].replace(" ", ""))[:12]
            if r > 0 and self.date[r - 1][7] != self.date[r][7]:
                self.tot_day += 1
            if r > 0 and self.date[r - 1][5] != self.date[r][5]:
                self.tot_month += 1
            if r > 0 and self.date[r - 1][3] != self.date[r][3]:
                self.tot_year += 1

    def manage_date(self):
        if self.cdatai > 0:
            if self.date[self.cdatai - 1][7] != self.date[self.cdatai][7]:
                self.day += 1
                self.day_changed = True
                return 1
            if self.date[self.cdatai - 1][5] != self.date[self.cdatai][5]:
                self.month += 1
                self.day = 1
                return 1
            if self.date[self.cdatai - 1][3] != self.date[self.cdatai][3]:
                self.year += 1
                self.month = 1
                return 1
            self.day_changed = False
            return 0
