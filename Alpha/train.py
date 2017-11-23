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
        self.agent = Agent(self.window_size)
        self.stock_name = env.stock_name
        self.data = getStockDataVec(self.stock_name)
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

    def update_env(self, env):
        env.POS_SELL = self.env.POS_SELL
        env.POS_BUY = self.env.POS_BUY
        env.cdatai = self.env.cdatai
        env.data = self.l
        env.contract_price = self.contract_price
        env.max_order = self.max_order
        env.spread = self.spread
        env.total_profit = self.total_profit
        env.reward = self.reward
        env.profit = self.profit
        env.buy_price = self.buy_price
        env.sell_price = self.sell_price
        env.pause = self.b
        env.corder = self.corder
        env.inventory = self.agent.inventory
        env.cdata = self.cdata

    def src_sell(self, inventory):
        for i  in range(len(inventory)):
            if "SELL" in inventory.loc[i]:
                return (i)
        return (-1)

    def src_buy(self, inventory):
        for i  in range(len(inventory)):
            if "BUY" in inventory.loc[i]:
                return (i)
        return (-1)

    def training(self):
        for e in range(self.episode_count + 1):

            if self.b == 1:
                while (self.b==1):
                    time.sleep(self.b)

            print ("Episode " + str(e) + "/" + str(self.episode_count))
            state = getState(self.data, 0, self.window_size + 1)
            self.agent.inventory = pd.DataFrame(columns = self.columns)

            for t in range(self.l):
                self.env.cdatai = t
                self.cdata = self.data[t]
                self.env.POS_SELL = -1
                self.env.POS_BUY = -1

                if self.b == 1:
                    while (self.b==1):
                        time.sleep(self.b)

                POS = len(self.agent.inventory['POS'])
                action = self.agent.act(state)
                next_state = getState(self.data, t + 1, self.window_size + 1)
                self.buy_price = float(self.data[t]) + self.spread / 2
                self.sell_price = float(self.data[t]) - self.spread / 2
                self.reward = 0
                self.profit = 0

                if action == 1: # buy
                    self.corder = "BUY"
                    POS_SELL = self.src_sell(self.agent.inventory['POS'])
                    self.env.POS_SELL = POS_SELL
                    if POS_SELL == -1:
                        buy = (pd.DataFrame([self.buy_price], columns = [self.columns[0]])).join(pd.DataFrame(["BUY"], columns = [self.columns[1]]))
                        self.agent.inventory = self.agent.inventory.append(buy, ignore_index=True)
                    else:
                        self.profit = (self.agent.inventory['Price'][POS_SELL] - self.sell_price) * self.contract_price
                        self.total_profit += self.profit
                        self.agent.inventory = (self.agent.inventory.drop(self.agent.inventory.index[POS_SELL])).reset_index(drop=True)
                    if self.profit > 0:
                        self.reward = self.profit
                    if POS > self.max_order:
                        self.reward = -(POS)
                   # print ("Buy: " + formatPrice(self.buy_price) + "| Profit: " + formatPrice(self.profit), "| total:", formatPrice(self.total_profit)," Data :", t, "/", self.l)

                elif action == 2: # sell
                    self.corder = "SELL"
                    POS_BUY = self.src_buy(self.agent.inventory['POS'])
                    self.env.POS_BUY = POS_BUY
                    if POS_BUY == -1:
                        sell = (pd.DataFrame([self.sell_price], columns = [self.columns[0]])).join(pd.DataFrame(["SELL"], columns = [self.columns[1]]))
                        self.agent.inventory = self.agent.inventory.append(sell, ignore_index=True)
                    else:
                        self.profit = (self.buy_price - self.agent.inventory['Price'][POS_BUY]) * self.contract_price
                        self.total_profit += self.profit
                        self.agent.inventory = (self.agent.inventory.drop(self.agent.inventory.index[POS_BUY])).reset_index(drop=True)
                    if self.profit > 0:
                        self.reward = self.profit
                    if POS > self.max_order:
                        self.reward = -(POS)
                    #print ("Sell: " + formatPrice(self.sell_price) + "| Profit: " + formatPrice(self.profit), "| total:", formatPrice(self.total_profit)," Data :", t, "/", self.l)
                else:
                    if POS > self.max_order:
                        self.reward = -POS
                    else:
                        self.reward = -1
                done = True if t == self.l - 1 else False
                self.agent.memory.append((state, action, self.reward, next_state, done))
                state = next_state
                if len(self.agent.memory) > self.batch_size:
                    self.agent.expReplay(self.batch_size)
                self.update_env(self.env)
                self.interface.update()

            if e % 10 == 0:
                self.agent.model.save("models/model_" + str(self.stock_name) + "_ws_" + str(self.window_size) +"_ep_" + str(e))

        

'''
if len(sys.argv) != 4:
	print ("Usage: python train.py [stock] [window] [episodes]")
	exit()


t = train(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
'''
