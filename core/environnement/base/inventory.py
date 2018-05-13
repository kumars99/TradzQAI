import pandas as pd

class Inventory(object):

    def __init__(self):
        self.columns = ['Price', 'POS', 'Order', 'Fee']
        self.inventory = pd.DataFrame(columns = self.columns)

        self.last_trade = dict(
            open = dict(
                price = 0,
                pos = "",
                fee = 0
            ),
            close = dict(
                price = 0,
                pos = "",
                fee = 0
            ),
            profit = 0,
            fee = 0
        )

        self.last_closed_order = dict(
            price = 0,
            pos = "",
            fee = 0,
            order = 0
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

    def save_last_closing(self, POS):
        '''Save last trade and drop it from inventory'''
        self.last_closed_order['price'] = (self.inventory['Price']).iloc[POS]
        self.last_closed_order['pos'] = (self.inventory['POS']).iloc[POS]
        self.last_closed_order['order'] = (self.inventory['Order']).iloc[POS]
        self.last_closed_order['fee'] = (self.inventory['Fee']).iloc[POS]
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

    def add_last_trade(self, prices, pip_value, fee):
        self.last_trade['open']['price'] = self.last_closed_order['price']
        self.last_trade['open']['pos'] = self.last_closed_order['pos']
        self.last_trade['open']['fee'] = self.last_closed_order['fee']
        if "SELL" in self.last_closed_order['pos']:
            self.last_trade['close']['price'] = prices['buy']
            self.last_trade['close']['pos'] = "BUY"
            self.last_trade['profit'] = (self.last_closed_order['price'] - prices['buy']) * pip_value * self.last_closed_order['order']
            self.last_trade['close']['pos'] = fee
        elif "BUY" in self.last_closed_order['pos']:
            self.last_trade['close']['price'] = prices['sell']
            self.last_trade['close']['pos'] = "SELL"
            self.last_trade['profit'] = (prices['sell'] - self.last_closed_order['price']) * pip_value * self.last_closed_order['order']
            self.last_trade['close']['fee'] = fee
        self.last_trade['fee'] = self.last_trade['close']['fee'] + self.last_trade['open']['fee']
        self.trade_history.append(self.last_trade)

    def manage_trade(self, env, profit, fee):
        env.wallet.profit['current'] = (profit * self.inventory['Order'].iloc[0] * env.contract_settings['pip_value']) + fee
        if env.wallet.profit['current'] < 0.00:
            env.trade['loss'] += 1
            env.daily_trade['loss'] += 1
            env.reward['current'] = profit + fee
        elif env.wallet.profit['current'] > 0.00 :
            env.trade['win'] += 1
            env.daily_trade['win'] += 1
            env.reward['current'] = profit + fee
        else:
            env.trade['draw'] += 1
            env.daily_trade['draw'] += 1
        env.closed = True

    def trade_closing(self, env):
        if len(self.inventory) > 0 and env.step_left == len(self.inventory):
            current = self.inventory['Price'].iloc[0]
            if "SELL" in self.inventory['POS'].iloc[0]:
                ret = current - env.price['sell']
            elif "BUY" in self.inventory['POS'].iloc[0]:
                ret = env.price['buy'] - current
            fee = env.wallet.calc_fees(ret * self.inventory['Order'].iloc[0])
            self.manage_trade(env, ret, fee)
            self.save_last_closing(0)
            self.add_last_trade(env.price, env.contract_settings['pip_value'], fee)
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
                fee = env.wallet.calc_fees(ret * self.inventory['Order'].iloc[i])
                self.manage_trade(env, ret, fee)
                self.save_last_closing(i)
                self.add_last_trade(env.price, env.contract_settings['pip_value'], fee)
                return True
        return False

    def inventory_managment(self, env):
        POS = len(self.inventory['POS']) # Number of contract in inventory
        if 1 == env.action: # Buy
            POS_SELL = self.src_sell() # Check if SELL order in inventory
            if POS_SELL == -1 and POS < env.wallet.risk_managment['current_max_pos'] and env.step_left > env.wallet.risk_managment['current_max_pos']: # Open order
                #buy = [env.price['buy'], "BUY", env.wallet.risk_managment['max_order_size'], env.wallet.calc_fees(env.wallet.risk_managment['max_order_size'] * env.price['buy'])]
                buy = (((pd.DataFrame([env.price['buy']], columns = [self.columns[0]])).join(pd.DataFrame(["BUY"],
                columns = [self.columns[1]]))).join(pd.DataFrame([env.wallet.risk_managment['max_order_size']],
                columns = [self.columns[2]]))).join(pd.DataFrame([env.wallet.calc_fees(env.wallet.risk_managment['max_order_size'] * env.price['buy'])],
                columns = [self.columns[3]]))
                #self.inventory = self.inventory.append(pd.DataFrame(buy, columns=self.columns), ignore_index=True)
                self.inventory = self.inventory.append(buy, ignore_index=True)
            elif POS_SELL != -1:# Close order in inventory
                '''Selling order from inventory list
                Calc profit and total profit
                Add last Sell order to env'''
                ret = self.inventory['Price'][POS_SELL] - env.price['sell']
                fee = env.wallet.calc_fees(ret * self.inventory['Order'].iloc[POS_SELL])
                self.manage_trade(env, ret, fee)
                self.save_last_closing(POS_SELL)
                self.add_last_trade(env.price, env.contract_settings['pip_value'], fee)
            else:
                env.reward['current'] = 0

        elif 2 == env.action: # Sell
            POS_BUY = self.src_buy() # Check if BUY order in inventory
            if POS_BUY == -1 and POS < env.wallet.risk_managment['current_max_pos'] and env.contract_settings['allow_short'] is True and env.wallet.risk_managment['current_max_pos'] and env.step_left > env.wallet.risk_managment['current_max_pos']: #Open order
                #sell = [env.price['sell'], "SELL", env.wallet.risk_managment['max_order_size'], env.wallet.calc_fees(env.wallet.risk_managment['max_order_size'] * env.price['sell'])]
                sell = (((pd.DataFrame([env.price['sell']], columns = [self.columns[0]])).join(pd.DataFrame(["SELL"],
                    columns = [self.columns[1]]))).join(pd.DataFrame([env.wallet.risk_managment['max_order_size']],
                    columns = [self.columns[2]]))).join(pd.DataFrame([env.wallet.calc_fees(env.wallet.risk_managment['max_order_size'] * env.price['sell'])],
                    columns = [self.columns[3]]))
                #self.inventory = self.inventory.append(pd.DataFrame(sell, columns=self.columns), ignore_index=True)
                self.inventory = self.inventory.append(sell, ignore_index=True)
            elif POS_BUY != -1:# Close order in inventory
                '''Selling order from inventory list
                Calc profit and total profit
                Add last Sell order to env'''
                ret = env.price['buy'] - self.inventory['Price'][POS_BUY]
                fee = env.wallet.calc_fees(ret * self.inventory['Order'].iloc[POS_BUY])
                self.manage_trade(env, ret, fee)
                self.save_last_closing(POS_BUY)
                self.add_last_trade(env.price, env.contract_settings['pip_value'], fee)
            else:
                env.reward['current'] = 0
        else: # Hold
            env.reward['current'] = 0
