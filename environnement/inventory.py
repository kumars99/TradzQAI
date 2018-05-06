import pandas as pd

class Inventory(object):

    def __init__(self, max_loss):
        self.max_loss = max_loss
        self.columns = ['Price', 'POS', 'Order']
        self.inventory = pd.DataFrame(columns = self.columns)

        self.last_trade = dict(
            open = dict(
                price = 0,
                pos = ""
            ),
            close = dict(
                price = 0,
                pos = ""
            ),
            profit = 0
        )

        self.last_closed_order = dict(
            price = 0,
            pos = ""
        )

        self.trade_history = []

    def reset(self):
        self.inventory = pd.DataFrame(columns = self.columns)

    def get_trade_history(self):
        return self.trade_history

    def get_inventory(self):
        return self.inventory

    def get_last_trade(self):
        return self.last_trade

    def add_last_trade(self, prices, pip_value):
        self.last_trade['open']['price'] = self.last_closed_order['price']
        self.last_trade['open']['pos'] = self.last_closed_order['pos']
        if "SELL" in self.last_closed_order['pos']:
            self.last_trade['close']['price'] = prices['buy']
            self.last_trade['close']['pos'] = "BUY"
            self.last_trade['profit'] = (self.last_closed_order['price'] - prices['buy']) * pip_value * self.last_closed_order['Order']
        elif "BUY" in self.last_closed_order['pos']:
            self.last_trade['close']['price'] = prices['sell']
            self.last_trade['close']['pos'] = "SELL"
            self.last_trade['profit'] = (prices['sell'] - self.last_closed_order['price']) * pip_value * self.last_closed_order['Order']
        self.trade_history.append(self.last_trade)

    def trade_closing(self, env):
        if len(self.inventory) > 0 and env.step_left == len(self.inventory):
            current = self.inventory['Price'].iloc[0]
            if "SELL" in self.inventory['POS'].iloc[0]:
                ret = current - env.price['sell']
            elif "BUY" in self.inventory['POS'].iloc[0]:
                ret = env.price['buy'] - current
            env.wallet.profit['current'] = ret * self.inventory['Order'].iloc[0] * env.contract_settings['pip_value']
            if env.wallet.profit['current'] < 0.00:
                env.trade['loss'] += 1
                env.daily_trade['loss'] += 1
                env.reward['current'] = ret
            elif env.wallet.profit['current'] > 0.00 :
                env.trade['win'] += 1
                env.daily_trade['win'] += 1
                env.reward['current'] = ret
            else:
                env.trade['draw'] += 1
                env.daily_trade['draw'] += 1
            self.save_last_closing(0)
            self.add_last_trade(env.price, env.contract_settings['pip_value'])
            return True
        return False


    def stop_loss(self, env):
        '''Stop loss'''
        current = 0
        for i in range(len(self.inventory)):
            current = self.inventory['Price'][i]
            if "SELL" in self.inventory['POS'][i]:
                ret = env.price['buy'] - current
            elif "BUY" in self.inventory['POS'][i]:
                ret = current - env.price['sell']
            if abs(ret) >= env.wallet.risk_managment['stop_loss'] and ret < 0:
                env.wallet.profit['current'] = ret * self.inventory['Order'][i] * env.contract_settings['pip_value']
                if env.wallet.profit['current'] < 0.00:
                    env.trade['loss'] += 1
                    env.daily_trade['loss'] += 1
                    env.reward['current'] = ret
                elif env.wallet.profit['current'] > 0.00 :
                    env.trade['win'] += 1
                    env.daily_trade['win'] += 1
                    env.reward['current'] = ret
                else:
                    env.trade['draw'] += 1
                    env.daily_trade['draw'] += 1
                self.save_last_closing(i)
                self.add_last_trade(env.price, env.contract_settings['pip_value'])
                return True
        return False

    def save_last_closing(self, POS):
        '''Save last trade and drop it from inventory'''
        self.last_closed_order['price'] = (self.inventory['Price']).iloc[POS]
        self.last_closed_order['pos'] = (self.inventory['POS']).iloc[POS]
        self.last_closed_order['Order'] = (self.inventory['Order']).iloc[POS]
        self.inventory = (self.inventory.drop(self.inventory.index[POS])).reset_index(drop=True)

    def src_sell(self):
        '''Search for first sell order'''
        for i  in range(len(self.inventory['POS'])):
            if "SELL" in self.inventory['POS'].loc[i]:
                return (i)
        return (-1)

    def src_buy(self):
        '''Search for first buy order'''
        for i  in range(len(self.inventory['POS'])):
            if "BUY" in self.inventory['POS'].loc[i]:
                return (i)
        return (-1)

    def inventory_managment(self, env):
        POS = len(self.inventory['POS']) # Number of contract in inventory
        if 1 == env.action: # Buy
            env.current_step['order'] = "BUY"
            POS_SELL = self.src_sell() # Check if SELL order in inventory
            env.POS_SELL = POS_SELL
            if POS_SELL == -1 and POS < env.wallet.risk_managment['current_max_pos'] and env.step_left > env.wallet.risk_managment['current_max_pos']: # Open order
                buy = ((pd.DataFrame([env.price['buy']], columns = [self.columns[0]])).join(pd.DataFrame(["BUY"], columns = [self.columns[1]]))).join(pd.DataFrame([env.wallet.risk_managment['max_order_size']], columns = [self.columns[2]]))
                self.inventory = self.inventory.append(buy, ignore_index=True)
            elif POS_SELL != -1:# Close order in inventory
                '''Selling order from inventory list
                Calc profit and total profit
                Add last Sell order to env'''
                env.wallet.profit['current'] = self.inventory['Price'][POS_SELL] - env.price['sell']
                if env.wallet.profit['current'] < 0.00:
                    env.trade['loss'] += 1
                    env.daily_trade['loss'] += 1
                    env.reward['current'] = env.wallet.profit['current']
                elif env.wallet.profit['current'] > 0.00 :
                    env.trade['win'] += 1
                    env.daily_trade['win'] += 1
                    env.reward['current'] = env.wallet.profit['current']
                else:
                    env.trade['draw'] += 1
                    env.daily_trade['draw'] += 1
                    env.reward['current'] = 0
                env.wallet.profit['current'] *= env.contract_settings['pip_value'] * self.inventory['Order'][POS_SELL]
                self.save_last_closing(POS_SELL)
                self.add_last_trade(env.price, env.contract_settings['pip_value'])
            else:
                env.reward['current'] = 0

        elif 2 == env.action: # Sell
            env.current_step['order'] = "SELL"
            POS_BUY = self.src_buy() # Check if BUY order in inventory
            env.POS_BUY = POS_BUY
            if POS_BUY == -1 and POS < env.wallet.risk_managment['current_max_pos'] and env.contract_settings['allow_short'] is True and env.wallet.risk_managment['current_max_pos'] and env.step_left > env.wallet.risk_managment['current_max_pos']: #Open order
                sell = ((pd.DataFrame([env.price['sell']], columns = [self.columns[0]])).join(pd.DataFrame(["SELL"], columns = [self.columns[1]]))).join(pd.DataFrame([env.wallet.risk_managment['max_order_size']], columns = [self.columns[2]]))
                self.inventory = self.inventory.append(sell, ignore_index=True)
            elif POS_BUY != -1:# Close order in inventory
                '''Selling order from inventory list
                Calc profit and total profit
                Add last Sell order to env'''
                env.wallet.profit['current'] = env.price['buy'] - self.inventory['Price'][POS_BUY]
                if env.wallet.profit['current'] < 0.00:
                    env.trade['loss'] += 1
                    env.daily_trade['loss'] += 1
                    env.reward['current'] = env.wallet.profit['current']
                elif env.wallet.profit['current'] > 0.00 :
                    env.trade['win'] += 1
                    env.daily_trade['win'] += 1
                    env.reward['current'] = env.wallet.profit['current']
                else:
                    env.trade['draw'] += 1
                    env.daily_trade['draw'] += 1
                    env.reward['current'] = 0
                env.wallet.profit['current'] *= env.contract_settings['pip_value'] * self.inventory['Order'][POS_BUY]
                self.save_last_closing(POS_BUY)
                self.add_last_trade(env.price, env.contract_settings['pip_value'])
            else:
                env.reward['current'] = 0
        else: # Hold
            env.reward['current'] = 0
