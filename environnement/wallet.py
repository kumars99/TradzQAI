from collections import deque

class Wallet(object):

    def __init__(self):
        self.lst_capital = []
        self.lst_return = deque(maxlen=1000)
        self.lst_mean_return = []
        self.lst_sharp_ratio = []
        self.profit = dict(
            current = 0,
            daily = 0,
            total = 0
        )
        self.risk_managment = dict(
            max_pos = 10,
            max_order_size = 1,
            current_max_pos = 0,
            exposure = 10,
            stop_loss = 20,
            capital_exposure = 0
        )
        self.settings = dict(
            capital = 20000,
            used_margin = 0,
            GL_pip = 0,
            GL_profit = 0
        )
        self.settings['saved_capital'] = self.settings['capital']
        self.settings['usable_margin'] = self.settings['capital']
        self.reset()

    def daily_reset(self):
        self.profit['current'] = 0
        self.profit['daily'] = 0

    def reset(self):
        self.settings['capital'] = self.settings['saved_capital']
        self.settings['used_margin'] = 0
        self.settings['GL_pip'] = 0
        self.settings['GL_profit'] = 0
        self.settings['usable_margin'] = self.settings['capital']
        self.risk_managment['max_order_size'] = 1
        self.risk_managment['current_max_pos'] = 0
        self.profit['total'] = 0

    def manage_wallet(self, inventory, price, contract_settings):
        avg = 0
        i = 0
        while i != len(inventory['POS']):
            avg += inventory['Price'][i]
            i += 1
        if i > 0:
            avg /= i
            if "SELL" in inventory['POS'][0]:
                self.risk_managment['GL_profit'] = (avg - price['sell']) * i * contract_settings['pip_value'] * self.risk_managment['max_order_size']
            elif "BUY" in inventory['POS'][0]:
                self.risk_managment['GL_profit'] = (price['buy'] - avg) * i * contract_settings['pip_value'] * self.risk_managment['max_order_size']
        else:
            self.risk_managment['GL_profit'] = 0
        self.settings['capital'] += self.profit['current']
        self.settings['used_margin'] = (len(inventory['POS']) * contract_settings['contract_price'] * self.risk_managment['max_order_size']) + (self.risk_managment['GL_profit'] * -1)
        self.settings['usable_margin'] = self.risk_managment['capital_exposure'] - self.settings['used_margin']
        if self.settings['used_margin'] < 0:
            self.settings['used_margin'] = 0

    def manage_exposure(self, contract_settings):
        self.risk_managment['capital_exposure'] = self.settings['capital'] - (self.settings['capital'] * (1 - (self.risk_managment['exposure'] / 100)))
        max_order_valid = self.risk_managment['capital_exposure'] // (contract_settings['contract_price'] + (self.risk_managment['stop_loss'] * contract_settings['pip_value']))
        if max_order_valid <= self.risk_managment['max_pos']:
            self.risk_managment['current_max_pos'] = max_order_valid
            self.risk_managment['max_order_size'] = 1
        else:
            self.risk_managment['current_max_pos'] = self.risk_managment['max_pos']
            extra_order = max_order_valid - self.risk_managment['max_pos']
            if extra_order >= self.risk_managment['max_pos']:
                self.risk_managment['max_order_size'] = int(max_order_valid // self.risk_managment['max_pos'])
            else:
                self.risk_managment['max_order_size'] = 1
