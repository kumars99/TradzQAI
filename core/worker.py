from math import *

import time
import pandas as pd
import sys
import os

from environnement import Environnement
from tools import *

from PyQt5.QtCore import *

class Worker(QThread):


    sig_step = pyqtSignal()
    sig_batch = pyqtSignal()
    sig_episode = pyqtSignal()

    def __init__(self, env):
        QThread.__init__(self)
        #self.interface = interface
        self.inventory_memory = []
        self.env = env
        self.columns = ['Price', 'POS', 'Order']
        self.action = 0
        self.series = 0

    def init_agent(self):
        if "eval" in self.env.mode:
            is_eval = True
        else:
            is_eval = False

        if self.env.model_name in self.env.agents:
            Agent = getattr(__import__("agents", fromlist=[self.env.model_name]), self.env.model_name)
        else:
            raise ValueError('could not import %s' % self.env.model_name)

        self.data, self.raw, self.env.date = getStockDataVec(self.env.stock_name)
        self.env.check_dates()
        self.env.data = len(self.data) - 1
        self.agent = Agent(getState(self.raw,
                                    0,
                                    self.env.window_size + 1),
                           env=self.env,
                           is_eval=is_eval)

        self.agent.mode = self.env.mode
        self.agent.build_model()
        if self.env.logger.model_summary_file:
            self.env.logger.save_model_summary(self.agent.model)

    def update_env(self):
        self.env.lst_reward.append(self.env.tot_reward)
        self.env.lst_return.append(self.env.total_profit)
        self.env.tot_reward += self.env.reward

    def pip_drawdown_checking(self):
        '''Prevent high drawdown'''
        c = 0
        for i in range(len(self.agent.inventory)):
            c = self.agent.inventory['Price'][i]
            if "SELL" in self.agent.inventory['POS'][i]:
                self.env.corder = "BUY"
                res = c - self.env.sell_price
            elif "BUY" in self.agent.inventory['POS'][i]:
                self.env.corder = "SELL"
                res = self.env.buy_price - c
            if abs(res) >= self.env.max_pip_drawdown and res < 0:
                self.env.profit = res * self.agent.inventory['Order'][i] * self.env.pip_value
                self.env.POS_SELL = i # Put check in env
                self.env.total_profit += self.env.profit
                #self.env.reward += 0.5 * res
                self.env.loose += 1
                self.save_last_closing(i)
                return 1
        return 0

    def inventory_managment(self):
        POS = len(self.agent.inventory['POS']) # Number of contract in inventory
        if 1 == self.action: # Buy
            self.env.corder = "BUY"
            POS_SELL = self.src_sell(self.agent.inventory['POS']) # Check if SELL order in inventory
            self.env.POS_SELL = POS_SELL # Put check in env

            if POS_SELL == -1 and POS < self.env.cmax_pos: # No SELL order in inventory
                buy = ((pd.DataFrame([self.env.buy_price], columns = [self.columns[0]])).join(pd.DataFrame(["BUY"], columns = [self.columns[1]]))).join(pd.DataFrame([self.env.max_order_size], columns = [self.columns[2]]))
                self.agent.inventory = self.agent.inventory.append(buy, ignore_index=True)

            elif POS_SELL != -1:# Sell order in inventory
                '''Selling order from inventory list
                Calc profit and total profit
                Add last Sell order to env'''
                #POS_SELL = self.src_best_buy(self.agent.inventory['Price'])
                self.env.profit = self.agent.inventory['Price'][POS_SELL] - self.env.sell_price
                if self.env.profit < 0.00:
                    self.env.loose += 1
                    self.env.daily_loose += 1
                    #self.env.reward += 0.5 * self.env.profit
                    #self.series = 0
                elif self.env.profit > 0.00 :
                    self.env.win += 1
                    self.env.daily_win += 1
                    self.env.reward += self.env.profit #+ int(sqrt(self.series))
                    #self.series += 1
                else:
                    self.env.draw += 1
                self.env.profit *= self.env.pip_value * self.agent.inventory['Order'][POS_SELL]
                self.env.total_profit += self.env.profit
                self.save_last_closing(POS_SELL)
            else: # Negative reward if overtaking
                self.env.reward -= 0.5

        elif 2 == self.action: # Sell
            self.env.corder = "SELL"
            POS_BUY = self.src_buy(self.agent.inventory['POS']) # Check if BUY order in inventory
            self.env.POS_BUY = POS_BUY # Put check in env

            if POS_BUY == -1 and POS < self.env.cmax_pos:# No BUY order in inventory
                sell = ((pd.DataFrame([self.env.sell_price], columns = [self.columns[0]])).join(pd.DataFrame(["SELL"], columns = [self.columns[1]]))).join(pd.DataFrame([self.env.max_order_size], columns = [self.columns[2]]))
                self.agent.inventory = self.agent.inventory.append(sell, ignore_index=True)

            elif POS_BUY != -1:# Sell order in inventory
                '''Selling order from inventory list
                Calc profit and total profit
                Add last Sell order to env'''
                #POS_BUY = self.src_best_sell(self.agent.inventory['Price'])
                self.env.profit = self.env.buy_price - self.agent.inventory['Price'][POS_BUY]
                if self.env.profit < 0:
                    self.env.loose += 1
                    self.env.daily_loose += 1
                    #self.env.reward += 0.5 * self.env.profit
                    #self.series = 0
                elif self.env.profit > 0 :
                    self.env.win += 1
                    self.env.daily_win += 1
                    self.env.reward += self.env.profit #+ int(sqrt(self.series))
                    #self.series += 1
                else:
                    self.env.draw += 1
                self.env.profit *= self.env.pip_value * self.agent.inventory['Order'][POS_BUY]
                self.env.total_profit += self.env.profit
                self.save_last_closing(POS_BUY)
            else: # Negative reward if overtaking
                self.env.reward -= 0.5
        else: # Hold
            self.env.reward = 0

    def save_last_closing(self, POS):
        '''Save last trade and drop it from inventory'''
        self.env.cd = (self.agent.inventory['Price']).iloc[POS]
        self.env.co = (self.agent.inventory['POS']).iloc[POS]
        self.agent.inventory = (self.agent.inventory.drop(self.agent.inventory.index[POS])).reset_index(drop=True)

    def src_best_sell(self, inventory):
        csell = []
        for i in inventory:
            csell.append(self.env.buy_price - i)
        return np.argmax(csell)

    def src_best_buy(self, inventory):
        cbuy = []
        for i in inventory:
            cbuy.append(i - self.env.buy_price)
        return np.argmax(cbuy)

    def src_sell(self, inventory):
        '''Search for first sell order'''
        for i  in range(len(inventory)):
            if "SELL" in inventory.loc[i]:
                return (i)
        return (-1)

    def src_buy(self, inventory):
        '''Search for first buy order'''
        for i  in range(len(inventory)):
            if "BUY" in inventory.loc[i]:
                return (i)
        return (-1)
