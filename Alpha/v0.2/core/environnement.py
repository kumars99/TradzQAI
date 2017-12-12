from tools.logger import *

import pandas as pd

from PyQt5.QtCore import *

class environnement(QObject):

    def __init__(self):
        super(QObject, self).__init__()

        # Soft settings

        self.name = "TradzQAI"
        self.version = "v0.2"
        self.v_state = "Alpha"

        # Environnement settings

        self.mode = ""
        self.stock_name = "DAX30_1M_2017_10_wi2"
        self.episode_count = 100
        self.window_size = 100
        self.batch_size = 32

        # Wallet settings

        self.spread = 1
        self.max_order_size = 1
        self.max_pos = 10
        self.cmax_pos = self.max_pos
        self.pip_value = 5
        self.contract_price = 125
        self.exposure = 10 # Exposure in percent
        self.max_pip_drawdown = 10

        # Wallet state

        self.capital = 100000
        self.cgl = 0
        self.dgl = 0
        self.usable_margin = self.capital
        self.used_margin = 0
        self.pip_gl = 0
        self.max_return = 0
        self.max_drawdown = 0

        # Agent state

        self.total_profit = 0
        self.reward = 0
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

        # Orders

        self.win = 0
        self.loose = 0
        self.draw = 0

        # Time

        self.start_t = 0
        self.loop_t = 0

        # List for graph building

        ## Daily list

        ### Overview list

        self.lst_data = []
        self.lst_inventory_len = []
        self.lst_profit = []
        self.lst_drawdown = []
        self.lst_win_order = []
        self.lst_loose_order = []
        self.lst_draw_order = []

        ### Model list

        self.lst_act = []
        self.lst_reward = []
        self.lst_act_predit = []
        self.lst_traget_predict = []
        self.lst_target = []
        self.lst_state = []
        self.lst_epsilon = []

        ## Episode list

        ### Historical list

        self.h_lst_reward = []
        self.h_lst_profit = []
        self.h_lst_win_order = []
        self.h_lst_loose_order = []
        self.h_lst_draw_order = []

        # Init logger

        #self.logs = logger(self)

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
            if len(ordr['Orders']) > 39:
                ordr = (ordr.drop(0)).reset_index(drop=True)
            tmp = pd.DataFrame(new, columns = ['Orders'])
            ordr = ordr.append(tmp, ignore_index=True)
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

    def manage_exposure(self):
        self.capital_exposure = self.capital - (self.capital * (1 - (self.exposure / 100)))
        max_order_valid = self.capital_exposure // (self.contract_price + (self.max_pip_drawdown * self.pip_value))
        if max_order_valid <= self.max_pos:
            self.cmax_pos = max_order_valid
        else:
            extra_order = max_order_valid - self.max_pos
            if extra_order >= self.max_pos:
                self.max_order_size = int(max_order_valid // self.max_pos)
