from agent.agent import Agent
from functions import *
import pandas as pd
import sys

if len(sys.argv) != 4:
	print ("Usage: python train.py [stock] [window] [episodes]")
	exit()

stock_name, window_size, episode_count = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])

agent = Agent(window_size)
data = getStockDataVec(stock_name)
l = len(data) - 1
batch_size = 32
contract_price = 5
columns = ['Price', 'POS']
max_order = 5
spread = 1
unposed = 1

def src_sell(inventory):
    i = 0
    while i  < len(inventory):
        if "SELL" in inventory.loc[i]:
            return (i)
        i += 1
    return (-1)

def src_buy(inventory):
    i = 0
    while i  < len(inventory):
        if "BUY" in inventory.loc[i]:
            return (i)
        i += 1
    return (-1)


for e in range(episode_count + 1):
        print ("Episode " + str(e) + "/" + str(episode_count))
        state = getState(data, 0, window_size + 1)

        total_profit = 0
        #agent.inventory = []
        agent.inventory = pd.DataFrame(columns = columns)

        for t in range(l):
            POS = len(agent.inventory['POS'])
            action = agent.act(state)
            #print (agent.inventory)

            # sit
            next_state = getState(data, t + 1, window_size + 1)
            reward = 0
            buy_price = float(data[t]) + spread / 2
            sell_price = float(data[t]) - spread / 2

            if action == 1: # buy
                unposed = 1
                POS_SELL = src_sell(agent.inventory['POS'])
                profit = 0
                if POS_SELL == -1:
                    buy = (pd.DataFrame([buy_price], columns = [columns[0]])).join(pd.DataFrame(["BUY"], columns = [columns[1]]))
                    agent.inventory = agent.inventory.append(buy, ignore_index=True)
                else:
                    profit = (agent.inventory['Price'][POS_SELL] - sell_price) * contract_price
                    total_profit += profit
                    agent.inventory = (agent.inventory.drop(agent.inventory.index[POS_SELL])).reset_index(drop=True)
                if POS > max_order:
                    reward = -(2**POS)
                reward += max(profit, 0)
                #agent.inventory.append(data[t])
                print ("Buy: " + formatPrice(buy_price) + "| Profit: " + formatPrice(profit), "| total:", formatPrice(total_profit)," Data :", t, "/", l)

            elif action == 2: # sell
                unposed = 1
                POS_BUY = src_buy(agent.inventory['POS'])
                profit = 0
                if POS_BUY == -1:
                    sell = (pd.DataFrame([sell_price], columns = [columns[0]])).join(pd.DataFrame(["SELL"], columns = [columns[1]]))
                    agent.inventory = agent.inventory.append(sell, ignore_index=True)
                else:
                    profit = (buy_price - agent.inventory['Price'][POS_BUY]) * contract_price
                    total_profit += profit
                    agent.inventory = (agent.inventory.drop(agent.inventory.index[POS_BUY])).reset_index(drop=True)
                if POS > max_order:
                    reward = -(2**POS)
                reward += max(profit, 0)
                '''
                bought_price = agent.inventory.pop(0)
                reward = max(data[t] - bought_price, 0)
                total_profit += data[t] - bought_price
                '''
                print ("Sell: " + formatPrice(sell_price) + "| Profit: " + formatPrice(profit), "| total:", formatPrice(total_profit)," Data :", t, "/", l)
            else:
                reward = -(POS * unposed)
                unposed += 1
            '''
                print ("Data :", t, "/", l)
            '''

            done = True if t == l - 1 else False
            agent.memory.append((state, action, reward, next_state, done))
            state = next_state

            if done:
                print ("--------------------------------")
                print ("Total Profit: " + formatPrice(total_profit))
                print ("--------------------------------")

            if len(agent.memory) > batch_size:
                agent.expReplay(batch_size)

        if e % 10 == 0:
            agent.model.save("models/model_" + str(stock_name) + "_ws_" + str(window_size) +"_ep_" + str(e))
