from agent import Agent
from functions import *
from math import *
import time
import pandas as pd
import sys
from environnement import *
from GUI.interface import *

class train(environnement):

    def __init__(self, env, interface):
        self.interface = interface
        if "eval" in env.mode:
            self.agent = Agent(env.window_size, is_eval=True, model_name= "model_" + str(env.stock_name) + "_ws_" + str(env.window_size))
        else:
            self.agent = Agent(env.window_size, model_name= "model_" + str(env.stock_name) + "_ws_" + str(env.window_size))
        self.agent.mode = env.mode
        self.row = pd.DataFrame()
        self.data, self.rsi = getStockDataVec(env.stock_name)
        self.l = len(self.data) - 1
        self.batch_size = 32
        self.columns = ['Price', 'POS']
        self.episode_count = env.episode_count
        self.b = 0
        self.corder = ""
        self.t = 0
        self.action = 0
        self.series = 0

    def update_env(self, env):
        env.data = self.l
        env.pause = self.b
        env.corder = self.corder
        env.inventory = self.agent.inventory

    def inventory_managment(self, order, env):
        POS = len(self.agent.inventory['POS']) # Number of contract in inventory
        if "BUY" in order:
            POS_SELL = self.src_sell(self.agent.inventory['POS']) # Check if SELL order in inventory
            env.POS_SELL = POS_SELL # Put check in env

            if POS_SELL == -1 and POS < env.max_order: # No SELL order in inventory
                buy = (pd.DataFrame([env.buy_price], columns = [self.columns[0]])).join(pd.DataFrame(["BUY"], columns = [self.columns[1]]))
                self.agent.inventory = self.agent.inventory.append(buy, ignore_index=True)

            elif POS_SELL != -1:# Sell order in inventory
                '''
                Selling order from inventory list
                Calc profit and total profit
                Add last Sell order to env
                '''
                env.profit = self.agent.inventory['Price'][POS_SELL] - env.sell_price
                if env.profit < 0:
                    env.loose += 1
                    self.series = 0
                elif env.profit > 0 :
                    env.reward += env.profit + int(sqrt(self.series))
                    env.win += 1
                    self.series += 1
                env.profit *= env.contract_price
                env.total_profit += env.profit
                env.cd = (self.agent.inventory['Price']).iloc[POS_SELL]
                self.agent.inventory = (self.agent.inventory.drop(self.agent.inventory.index[POS_SELL])).reset_index(drop=True)

        elif "SELL" in order:
            POS_BUY = self.src_buy(self.agent.inventory['POS']) # Check if BUY order in inventory
            env.POS_BUY = POS_BUY # Put check in env

            if POS_BUY == -1 and POS < env.max_order:# No BUY order in inventory
                sell = (pd.DataFrame([env.sell_price], columns = [self.columns[0]])).join(pd.DataFrame(["SELL"], columns = [self.columns[1]]))
                self.agent.inventory = self.agent.inventory.append(sell, ignore_index=True)

            elif POS_BUY != -1:# Sell order in inventory
                '''
                Selling order from inventory list
                Calc profit and total profit
                Add last Sell order to env
                '''
                env.profit = env.buy_price - self.agent.inventory['Price'][POS_BUY]
                if env.profit < 0:
                    env.loose += 1
                    self.series = 0
                elif env.profit > 0 :
                    env.reward += env.profit + int(sqrt(self.series))
                    env.win += 1
                    self.series += 1
                env.profit *= env.contract_price
                env.total_profit += env.profit
                env.cd = (self.agent.inventory['Price']).iloc[POS_BUY]
                self.agent.inventory = (self.agent.inventory.drop(self.agent.inventory.index[POS_BUY])).reset_index(drop=True)

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

    def training(self, env):
        for e in range(self.episode_count + 1):
            g = 0
            env.total_profit = 0
            env.win = 0
            env.loose = 0

            if self.b == 1:
                while (self.b==1):
                    time.sleep(self.b)

            #print ("Episode " + str(e) + "/" + str(self.episode_count))
            state = getState(self.data, 0, env.window_size + 1, self.rsi)
            for i in range(len(state[0]) - 1):
                env.lst_state.append(state[0][i])
            self.agent.inventory = pd.DataFrame(columns = self.columns) # Init agent inventory

            for t in range(self.l):
                self.t = t
                env.cdatai = t
                env.cdata = self.data[t]
                env.POS_SELL = -1
                env.POS_BUY = -1

                if self.b == 1:
                    while (self.b==1):
                        time.sleep(0.1)

                POS = len(self.agent.inventory['POS'])

                self.action = self.agent.act(state) # Get action from agent
                env.def_act(self.action)
                next_state = getState(self.data, t + 1, env.window_size + 1, self.rsi) # Get new state
                env.lst_state.append(next_state[0][len(next_state[0]) - 1])

                env.buy_price = self.data[t] - (env.spread / 2) # Update buy price with spread
                env.sell_price = self.data[t] + (env.spread / 2) # Update sell price with spread

                env.reward = 0 # Reset reward
                env.profit = 0 # Reset current profit

                if self.action == 1: # buy
                    g = 0
                    self.corder = "BUY"
                    self.inventory_managment(self.corder, env)

                elif self.action == 2: # sell
                    g = 0
                    self.corder = "SELL"
                    self.inventory_managment(self.corder, env)
                '''
                else:
                    if POS < self.max_order + 1:
                        self.reward = -(int(sqrt(g)))
                    else:
                        self.reward = -(int(sqrt(g)**sqrt(POS)))

                    g += 1
                '''
                self.update_env(env) # Updating env from agent for GUI
                self.interface.update() # Updating GUI from env

                done = True if t == self.l - 1 else False

                self.agent.memory.append((state, self.action, env.reward, next_state, done))
                state = next_state

                if "train" in env.mode:
                    if len(self.agent.memory) > self.batch_size:
                        self.agent.expReplay(self.batch_size)
                    if t % 10000 == 0 and t > 0 : # Save model all 10000 data
                        self.agent.model.save("models/model_" + str(env.stock_name) + "_ws_" + str(env.window_size))
                else:
                    time.sleep(0.01)
