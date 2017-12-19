from math import *

import time
import pandas as pd
import sys

from environnement import Environnement
from .agent import Agent
from tools import *
#from core.environnement import *

from PyQt5.QtCore import *

class Worker(QThread):

    sig_step = pyqtSignal()

    def __init__(self, env):
        QThread.__init__(self)
        #self.interface = interface
        self.inventory_memory = []
        self.env = env
        self.columns = ['Price', 'POS', 'Order']
        self.action = 0
        self.series = 0

    def init_agent(self):
        self.data, self.raw = getStockDataVec(self.env.stock_name)
        self.l = len(self.data) - 1
        if "eval" in self.env.mode:
            self.agent = Agent(getState(self.raw,
                                        0,
                                        self.env.window_size + 1),
                               env=self.env,
                               is_eval=True,
                               model_name= "model_" + \
                               str(self.env.stock_name) + "_ws_" + \
                               str(self.env.window_size))
        else:
            self.agent = Agent(getState(self.raw,
                                        0,
                                        self.env.window_size + 1),
                               env=self.env,
                               model_name= "model_" + \
                               str(self.env.stock_name) + "_ws_" + \
                               str(self.env.window_size))
        self.agent.mode = self.env.mode

    def update_env(self):
        self.env.data = self.l
        self.env.inventory = self.agent.inventory

    def pip_drawdown_checking(self):
        '''
        Prevent high drawdown
        '''
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
                self.env.reward -= 1
                self.env.loose += 1
                self.save_last_closing(i)
                return 1
        return 0

    def inventory_managment(self):
        POS = len(self.agent.inventory['POS']) # Number of contract in inventory
        if "BUY" in self.env.corder:
            POS_SELL = self.src_sell(self.agent.inventory['POS']) # Check if SELL order in inventory
            self.env.POS_SELL = POS_SELL # Put check in env

            if POS_SELL == -1 and POS < self.env.cmax_pos: # No SELL order in inventory
                buy = ((pd.DataFrame([self.env.buy_price], columns = [self.columns[0]])).join(pd.DataFrame(["BUY"], columns = [self.columns[1]]))).join(pd.DataFrame([self.env.max_order_size], columns = [self.columns[2]]))
                self.agent.inventory = self.agent.inventory.append(buy, ignore_index=True)

            elif POS_SELL != -1:# Sell order in inventory
                '''
                Selling order from inventory list
                Calc profit and total profit
                Add last Sell order to env
                '''
                POS_SELL = self.src_best_buy(self.agent.inventory['Price'])
                self.env.profit = self.agent.inventory['Price'][POS_SELL] - self.env.sell_price
                if self.env.profit < 0.00:
                    self.env.loose += 1
                    self.env.reward += 0.1 * self.env.profit
                    #self.series = 0
                elif self.env.profit > 0.00 :
                    self.env.win += 1
                    self.env.reward += self.env.profit #+ int(sqrt(self.series))
                    #self.series += 1
                else:
                    self.env.draw += 1
                self.env.profit *= self.env.pip_value * self.agent.inventory['Order'][POS_SELL]
                self.env.total_profit += self.env.profit
                self.save_last_closing(POS_SELL)
            else:
                self.env.reward -= 0.5

        elif "SELL" in self.env.corder:
            POS_BUY = self.src_buy(self.agent.inventory['POS']) # Check if BUY order in inventory
            self.env.POS_BUY = POS_BUY # Put check in env

            if POS_BUY == -1 and POS < self.env.cmax_pos:# No BUY order in inventory
                sell = ((pd.DataFrame([self.env.sell_price], columns = [self.columns[0]])).join(pd.DataFrame(["SELL"], columns = [self.columns[1]]))).join(pd.DataFrame([self.env.max_order_size], columns = [self.columns[2]]))
                self.agent.inventory = self.agent.inventory.append(sell, ignore_index=True)

            elif POS_BUY != -1:# Sell order in inventory
                '''
                Selling order from inventory list
                Calc profit and total profit
                Add last Sell order to env
                '''
                POS_BUY = self.src_best_sell(self.agent.inventory['Price'])
                self.env.profit = self.env.buy_price - self.agent.inventory['Price'][POS_BUY]
                if self.env.profit < 0:
                    self.env.loose += 1
                    self.env.reward += 0.1 * self.env.profit
                    #self.series = 0
                elif self.env.profit > 0 :
                    self.env.win += 1
                    self.env.reward += self.env.profit #+ int(sqrt(self.series))
                    #self.series += 1
                else:
                    self.env.draw += 1
                self.env.profit *= self.env.pip_value * self.agent.inventory['Order'][POS_BUY]
                self.env.total_profit += self.env.profit
                self.save_last_closing(POS_BUY)
            else:
                self.env.reward -= 0.5

    def save_last_closing(self, POS):
        '''
        Save last trade and drop it from inventory
        '''
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
        '''
        Search for first sell order
        '''
        for i  in range(len(inventory)):
            if "SELL" in inventory.loc[i]:
                return (i)
        return (-1)

    def src_buy(self, inventory):
        '''
        Search for first buy order
        '''
        for i  in range(len(inventory)):
            if "BUY" in inventory.loc[i]:
                return (i)
        return (-1)

    def run(self):
        self.init_agent()
        for e in range(self.env.episode_count + 1):
            self.env.total_profit = 0
            self.env.win = 0
            self.env.loose = 0
            self.env.draw = 0

            self.env.start_t = time.time()
            self.agent.inventory = pd.DataFrame(columns = self.columns) # Init agent inventory

            if self.env.pause == 1:
                while (self.env.pause == 1):
                    time.sleep(0.01)

            state = getState(self.raw,
                             0,
                             self.env.window_size + 1)

            for t in range(self.l):
                tmp = time.time()
                self.env.cdatai = t
                self.env.cdata = self.data[t]
                self.env.lst_data.append(self.env.cdata)
                self.env.POS_SELL = -1
                self.env.POS_BUY = -1

                if self.env.pause == 1:
                    while (self.env.pause == 1):
                        time.sleep(0.01)
                
                done = True if t == self.l - 1 else False

                POS = len(self.agent.inventory['POS'])

                self.action = self.agent.act(state) # Get action from agent
                self.env.def_act(self.action)
                # Get new state
                next_state = getState(self.raw,
                                      t + 1,
                                      self.env.window_size + 1)

                # Update buy price with spread
                self.env.buy_price = self.data[t] - (self.env.spread / 2)
                # Update sell price with spread
                self.env.sell_price = self.data[t] + (self.env.spread / 2)

                self.env.reward = 0 # Reset reward
                self.env.profit = 0 # Reset current profit

                self.env.manage_exposure()
                if self.pip_drawdown_checking() == 0:
                    if self.action == 1: # buy
                        self.env.corder = "BUY"
                        self.inventory_managment()

                    elif self.action == 2: # sell
                        self.env.corder = "SELL"
                        self.inventory_managment()

                    else:
                        self.env.reward -= 0.25

                self.update_env() # Updating env from agent for GUI
                self.env.manage_wallet()
                self.sig_step.emit() # Update GUI


                self.agent.memory.append((state,
                                          self.action,
                                          self.env.reward,
                                          next_state,
                                          done))
                state = next_state

                if "train" in self.env.mode:
                    if len(self.agent.memory) > self.env.batch_size:
                        self.agent.expReplay(self.env.batch_size)
                    if t % 1000 == 0 and t > 0 : # Save model all 1000 data
                        self.agent.model.save("models/model_" + str(self.env.stock_name) + "_ws_" + str(self.env.window_size))
                else:
                    time.sleep(0.01)

                self.env.loop_t = time.time() - tmp
