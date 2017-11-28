from agent import Agent
from functions import *
from math import *
import time
import pandas as pd
import sys
from environnement import *
from interface import *

class train(environnement):

    def __init__(self, env, interface):
        self.env = env
        self.interface = interface
        self.window_size = env.window_size
        self.stock_name = env.stock_name
        if "eval" in env.mode:
            self.agent = Agent(self.window_size, is_eval=True, model_name= "model_" + str(self.stock_name) + "_ws_" + str(self.window_size))
        else:
            self.agent = Agent(self.window_size, model_name= "model_" + str(self.stock_name) + "_ws_" + str(self.window_size))
        self.agent.mode = env.mode
        self.row = pd.DataFrame()
        self.data, self.rsi = getStockDataVec(self.stock_name)
        self.l = len(self.data) - 1
        self.batch_size = 32
        self.contract_price = env.contract_price
        self.columns = ['Price', 'POS']
        self.max_order = env.max_order
        self.spread = env.spread
        self.episode_count = env.episode_count
        self.total_profit = env.total_profit
        self.reward = env.reward
        self.profit = env.profit
        self.buy_price = env.buy_price
        self.sell_price = env.sell_price
        self.b = 0
        self.corder = ""
        self.cdata = 0
        self.cd = 0
        self.t = 0
        self.win = env.win
        self.loose_r = env.loose_r
        self.action = 0

    def update_env(self, env):
        env.POS_SELL = self.env.POS_SELL
        env.POS_BUY = self.env.POS_BUY
        env.cdatai = self.env.cdatai
        env.win = self.win
        env.loose_r = self.loose_r
        env.data = self.l
        env.total_profit = self.total_profit
        env.reward = self.reward
        env.profit = self.profit
        env.buy_price = self.buy_price
        env.sell_price = self.sell_price
        env.pause = self.b
        env.corder = self.corder
        env.inventory = self.agent.inventory
        env.cdata = self.cdata
        env.cd = self.cd
        env.def_act(self.action)

    def inventory_managment(self, order):
        POS = len(self.agent.inventory['POS']) # Number of contract in inventory
        if "BUY" in order:
            POS_SELL = self.src_sell(self.agent.inventory['POS']) # Check if SELL order in inventory
            self.env.POS_SELL = POS_SELL # Put check in env

            if POS_SELL == -1 and POS < self.max_order: # No SELL order in inventory
                buy = (pd.DataFrame([self.buy_price], columns = [self.columns[0]])).join(pd.DataFrame(["BUY"], columns = [self.columns[1]]))
                self.agent.inventory = self.agent.inventory.append(buy, ignore_index=True)
                #self.reward += 1
                #self.reward_managment(order, (self.row['RSI']).iloc[self.t], (self.row['Volatility']).iloc[self.t])

            elif POS_SELL != -1:# Sell order in inventory
                '''
                Selling order from inventory list
                Calc profit and total profit
                Add last Sell order to env
                '''
                #self.reward_managment("SELL", (self.row['RSI']).iloc[self.t], (self.row['Volatility']).iloc[self.t])
                self.profit = self.agent.inventory['Price'][POS_SELL] - self.sell_price
                if self.profit < 0:
                    self.loose_r += 1
                elif self.profit > 0 :
                    self.reward += self.profit
                    self.win += 1
                self.profit *= self.contract_price
                self.total_profit += self.profit
                self.cd = (self.agent.inventory['Price']).iloc[POS_SELL]
                self.agent.inventory = (self.agent.inventory.drop(self.agent.inventory.index[POS_SELL])).reset_index(drop=True)

            '''
            Add profit reward
            '''
            '''
            self.reward += self.profit

            if POS > self.max_order and POS_SELL == -1:
            '''
            '''
            Add a negativ reward for contract overtaking
            '''
            #self.reward += -(int(sqrt(POS**self.contract_price)))

        elif "SELL" in order:
            POS_BUY = self.src_buy(self.agent.inventory['POS']) # Check if BUY order in inventory
            self.env.POS_BUY = POS_BUY # Put check in env

            if POS_BUY == -1 and POS < self.max_order:# No BUY order in inventory
                sell = (pd.DataFrame([self.sell_price], columns = [self.columns[0]])).join(pd.DataFrame(["SELL"], columns = [self.columns[1]]))
                #self.reward_managment(order, (self.row['RSI']).iloc[self.t], (self.row['Volatility']).iloc[self.t])
                self.agent.inventory = self.agent.inventory.append(sell, ignore_index=True)
                #self.reward += 1

            elif POS_BUY != -1:# Sell order in inventory
                '''
                Selling order from inventory list
                Calc profit and total profit
                Add last Sell order to env
                '''
                #self.reward_managment("BUY", (self.row['RSI']).iloc[self.t], (self.row['Volatility']).iloc[self.t])
                self.profit = self.buy_price - self.agent.inventory['Price'][POS_BUY]
                if self.profit < 0:
                    self.loose_r += 1
                elif self.profit > 0 :
                    self.reward += self.profit
                    self.win += 1
                self.profit *= self.contract_price
                self.total_profit += self.profit
                self.cd = (self.agent.inventory['Price']).iloc[POS_BUY]
                self.agent.inventory = (self.agent.inventory.drop(self.agent.inventory.index[POS_BUY])).reset_index(drop=True)
            

            '''
            Add profit reward
            '''
            #self.reward += self.profit

            #if POS > self.max_order and POS_BUY == -1:
            '''
            Add a negativ reward for contract overtaking
            '''
            #self.reward += -(int(sqrt(POS**self.contract_price)))

    def reward_managment(self, POS, RSI, vol):
        '''
        oo = ordonner a l'origine
        cd = coefficient directeur
        f(x) = ax+b
        f(y) = sqrt(f(x)*v)
        '''

        if "BUY" in POS:
            oo = 100
            cd = -1

        elif "SELL" in POS:
            oo = 0
            cd = 1

        self.reward += int((cd * RSI + oo ) * vol)


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

    def training(self):
        for e in range(self.episode_count + 1):
            g = 0
            self.env.win = 0
            self.env.loose_r = 0
            self.total_profit = 0
            self.win = 0
            self.loose_r = 0

            if self.b == 1:
                while (self.b==1):
                    time.sleep(self.b)

            #print ("Episode " + str(e) + "/" + str(self.episode_count))
            state = getState(self.data, 0, self.window_size + 1, self.rsi)
            self.agent.inventory = pd.DataFrame(columns = self.columns) # Init agent inventory

            for t in range(self.l):
                self.t = t
                self.env.cdatai = t
                self.cdata = self.data[t]
                self.env.POS_SELL = -1
                self.env.POS_BUY = -1

                if self.b == 1:
                    while (self.b==1):
                        time.sleep(0.1)

                POS = len(self.agent.inventory['POS'])

                self.action = self.agent.act(state) # Get action from agent
                next_state = getState(self.data, t + 1, self.window_size + 1, self.rsi) # Get new state

                self.buy_price = self.data[t] - (self.spread / 2) # Update buy price with spread
                self.sell_price = self.data[t] + (self.spread / 2) # Update sell price with spread

                self.reward = 0 # Reset reward
                self.profit = 0 # Reset current profit

                if self.action == 1: # buy
                    g = 0
                    self.corder = "BUY"
                    self.inventory_managment(self.corder)

                elif self.action == 2: # sell
                    g = 0
                    self.corder = "SELL"
                    self.inventory_managment(self.corder)
                '''
                else:
                    if POS < self.max_order + 1:
                        self.reward = -(int(sqrt(g)))
                    else:
                        self.reward = -(int(sqrt(g)**sqrt(POS)))

                    g += 1
                '''
                self.update_env(self.env) # Updating env from agent for GUI
                self.interface.update() # Updating GUI from env

                done = True if t == self.l - 1 else False

                self.agent.memory.append((state, self.action, self.reward, next_state, done))
                state = next_state

                if "train" in self.env.mode:
                    if len(self.agent.memory) > self.batch_size:
                        self.agent.expReplay(self.batch_size)
                    if t % 10000 == 0 and t > 0 : # Save model all 10000 data
                        self.agent.model.save("models/model_" + str(self.stock_name) + "_ws_" + str(self.window_size))
