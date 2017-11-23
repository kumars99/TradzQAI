from agent import Agent
from functions import *
from math import *
import pandas as pd
import sys


class train():

    def __init__(self, stock_name, window_size, episode_count):
        self.agent = Agent(window_size)
        self.stock_name = stock_name
        self.data = getStockDataVec(stock_name)
        self.l = len(self.data) - 1
        self.batch_size = 32
        self.contract_price = 5
        self.columns = ['Price', 'POS']
        self.max_order = 5
        self.spread = 1
        self.episode_count = episode_count
        self.window_size = window_size
        self.total_profit = 0
        self.reward = 0
        self.profit = 0
        self.buy_price = 0
        self.sell_price = 0

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

            print ("Episode " + str(e) + "/" + str(self.episode_count))
            state = getState(self.data, 0, self.window_size + 1)
            self.agent.inventory = pd.DataFrame(columns = self.columns)

            for t in range(self.l):

                POS = len(self.agent.inventory['POS'])
                action = self.agent.act(state)
                next_state = getState(self.data, t + 1, self.window_size + 1)
                self.buy_price = float(self.data[t]) + self.spread / 2
                self.sell_price = float(self.data[t]) - self.spread / 2
                self.reward = 0
                self.profit = 0

                if action == 1: # buy
                    POS_SELL = self.src_sell(self.agent.inventory['POS'])
                    if POS_SELL == -1:
                        buy = (pd.DataFrame([self.buy_price], columns = [self.columns[0]])).join(pd.DataFrame(["BUY"], columns = [self.columns[1]]))
                        self.agent.inventory = self.agent.inventory.append(buy, ignore_index=True)
                    else:
                        self.profit = (self.agent.inventory['Price'][POS_SELL] - self.sell_price) * self.contract_price
                        self.total_profit += self.profit
                        self.agent.inventory = (self.agent.inventory.drop(self.agent.inventory.index[POS_SELL])).reset_index(drop=True)
                    if POS > self.max_order:
                        self.reward = -(POS)
                    if self.profit > 0:
                        self.reward += self.profit
                    print ("Buy: " + formatPrice(self.buy_price) + "| Profit: " + formatPrice(self.profit), "| total:", formatPrice(self.total_profit)," Data :", t, "/", self.l)

                elif action == 2: # sell
                    POS_BUY = self.src_buy(self.agent.inventory['POS'])
                    if POS_BUY == -1:
                        sell = (pd.DataFrame([self.sell_price], columns = [self.columns[0]])).join(pd.DataFrame(["SELL"], columns = [self.columns[1]]))
                        self.agent.inventory = self.agent.inventory.append(sell, ignore_index=True)
                    else:
                        self.profit = (self.buy_price - self.agent.inventory['Price'][POS_BUY]) * self.contract_price
                        self.total_profit += self.profit
                        self.agent.inventory = (self.agent.inventory.drop(self.agent.inventory.index[POS_BUY])).reset_index(drop=True)
                    if POS > self.max_order:
                        self.reward = -(POS)
                    if self.profit > 0:
                        self.reward += self.profit
                    print ("Sell: " + formatPrice(self.sell_price) + "| Profit: " + formatPrice(self.profit), "| total:", formatPrice(self.total_profit)," Data :", t, "/", self.l)
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
            if e % 10 == 0:
                self.agent.model.save("models/model_" + str(self.stock_name) + "_ws_" + str(self.window_size) +"_ep_" + str(e))
        


if len(sys.argv) != 4:
	print ("Usage: python train.py [stock] [window] [episodes]")
	exit()


t = train(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
t.training()
