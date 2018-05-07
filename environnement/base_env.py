from tools import Logger
from tools import *
from .inventory import Inventory
from .wallet import Wallet

import pandas as pd
import numpy as np
from collections import deque
from tqdm import tqdm

import os
import sys
import time

class Environnement:

    def __init__(self, gui):

        self._name = os.path.basename(__file__).replace(".py", "")
        self.name = "TradzQAI"
        self.version = "v0.2"
        self.v_state = "Alpha"
        self._platform = sys.platform
        self.agents = self.src_agents()
        self.gui = gui

        self.model = None
        self.model_name = "PPO"
        self.mode = ""

        self.stock_name = "DAX30_TICK_2018_03_15"
        self.model_dir = self.model_name + "_" + self.stock_name.split("_")[0]
        self.episode_count = 500
        self.window_size = 10
        self.batch_size = 32

        self.daily_trade = dict(
            win = 0,
            loss = 0,
            draw = 0,
            total = 0
        )

        self.reward = dict(
            current = 0,
            daily = 0,
            total = 0
        )

        self.current_step = dict(
            order = "",
            episode = 0,
            step = -1
        )

        self.trade = dict(
            win = 0,
            loss = 0,
            draw = 0,
            total = 0,
        )

        self.date = dict(
            day = 1,
            month = 1,
            year = 1,
            total_minutes = 1,
            total_day = 1,
            total_month = 1,
            total_year = 1
        )

        self.price = dict(
            buy = 0,
            sell = 0
        )

        self.last_closed_order = dict(
            current_price = 0,
            current_pos = ""
        )

        self.step_left = 0
        self.max_return = 0
        self.max_drawdown = 0
        self.pause = 0
        self.action = None
        self.data = None
        self.POS_BUY = -1
        self.POS_SELL = -1
        self.start_t = 0
        self.loop_t = 0
        self._date = None
        self.mod_ordr = False
        self.day_changed = False
        self.new_episode = False

        self.lst_data = []
        self.lst_inventory_len = []
        self.lst_return = deque(maxlen=1000)
        self.lst_mean_return = []
        self.lst_sharp_ratio = []
        self.lst_drawdown = []
        self.lst_win_order = []
        self.lst_loose_order = []
        self.lst_draw_order = []
        self.lst_capital = []

        self.lst_act = deque(maxlen=1000)
        self.lst_reward = deque(maxlen=1000)
        self.lst_state = deque(maxlen=1000)

        self.train_in = []
        self.train_out = []

        self.time = None
        self.lst_data_full = deque(maxlen=100)
        self.lst_data_preprocessed = []
        self.offset = 0

        self.tensorOCHL = [[] for _ in range(4)]


        self.lst_reward_daily = []

        self.readed = None

        self.wallet = Wallet()
        self.inventory = Inventory(self.wallet.risk_managment['stop_loss'])
        self.data, self.raw, self._date = getStockDataVec(self.stock_name)

        self.settings = dict(
            network = self.get_network(),
            agent = self.get_agent_settings(),
            env = self.get_env_settings()
        )

        self.logger = Logger()
        self.logger._load_conf(self)
        self.check_dates()

    def get_network(self):

        network = [dict(type='dense', size=64, activation='relu'),
                   dict(type='dense', size=32, activation='relu'),
                   dict(type='dense', size=8, activation='relu')]



        '''

        network = [dict(
                type = "conv1d",
                size = 64,
                window = 4,
                stride = 1,
                padding = "SAME"
            ),
            dict(
                type = "conv1d",
                size = 64,
                window = 2,
                stride = 1,
                padding = "SAME"
            ),
            dict(
                type = "flatten"
            ),
            dict(
                type="dense",
                size=128,
                activation="relu"
            )
        ]
        '''


        return network

    def get_agent_settings(self):
        self.update_mode = dict(
            unit = 'timesteps',
            batch_size = self.batch_size,
            frequency = self.batch_size // 8
        )

        self.summarizer = dict(
            directory="./board/",
            steps=1000,
            labels=['configuration',
                    'gradients_scalar',
                    'regularization',
                    'inputs',
                    'losses',
                    'variables']
        )

        self.memory=dict(
            type='latest',
            include_next_states=True,
            capacity=((len(self.data) - 1) * self.batch_size)
        )

        self.hyperparameters = dict(
            update_rate = 1e-3,
            learning_rate = 1e-3,
            gamma = 0.97,
            epsilon = 1.0,
            epsilon_min = 1e-2,
            epsilon_decay = 0.995
        )

        self.exploration = dict(
            type = 'epsilon_anneal',
            initial_epsilon = self.hyperparameters['epsilon'],
            final_epsilon = self.hyperparameters['epsilon_min']
        )

        self.optimizer = dict(
            type='adam',
            learning_rate=self.hyperparameters['learning_rate']
        )

        agent = [self.hyperparameters,
                 self.exploration,
                 self.update_mode,
                 self.summarizer,
                 self.memory,
                 self.optimizer]

        return agent

    def get_env_settings(self):
        self.contract_settings = dict(
            pip_value = 5,
            contract_price = 125,
            spread = 1,
            allow_short = False
        )

        self.meta = dict(
            window_size = self.window_size,
            batch_size = self.batch_size
        )

        env = [self.contract_settings,
               self.wallet.settings,
               self.wallet.risk_managment,
               self.meta]

        return env

    def _pause(self):
        self.pause = 1

    def _resume(self):
        self.pause = 0

    def init_logger(self):
        self.logger.init_saver(self)
        self.logger._load()
        #self.logger.new_logs(self._name)

    def def_act(self):
        if self.action == 1:
            self.act = "BUY"
            self.lst_act.append(1)
        elif self.action == 2:
            self.act = "SELL"
            self.lst_act.append(-1)
        else:
            self.act = "HOLD"
            self.lst_act.append(0)

    def manage_orders(self, ordr):
        if self.POS_BUY > -1 or self.POS_SELL > -1:
            last_trade = self.inventory.get_last_trade()
            new = [str(last_trade['open']['pos']) \
                   + " : " \
                   + '{:.2f}'.format(last_trade['open']['price']) \
                   + " -> " \
                   + str(last_trade['close']['pos']) \
                   + " : " \
                   + '{:.2f}'.format(last_trade['close']['price']) \
                   + " | Profit : " \
                   + '{:.2f}'.format(self.wallet.profit['current'])]

            if len(ordr['Orders']) > 37:
                ordr = (ordr.drop(0)).reset_index(drop=True)
            tmp = pd.DataFrame(new, columns = ['Orders'])
            ordr = ordr.append(tmp, ignore_index=True)
            self.mod_ordr = True
        else:
            self.mod_ordr = False
        return ordr

    def src_agents(self):
        ignore = ['agent.py', '__init__.py', '__pycache__']
        valid = []
        for f in os.listdir("agents"):
            if f not in ignore:
                valid.append(f.replace(".py", ""))
        return valid

    def check_dates(self):
        self._date = self._date.apply(lambda x: x.replace(" ", "")[:12])
        if self.gui == 0:
            ldate = tqdm(range(1, len(self._date) - 1), desc = "Checking dates ")
        else:
            ldate = range(1, len(self._date) - 1)
        for r in ldate:
            date_c = self._date[r]
            date_p = self._date[r - 1]
            if date_p[11] != date_c[11]:
                self.date['total_minutes'] += 1
            if date_p[7] != date_c[7]:
                self.date['total_day'] += 1
            if date_p[5] != date_c[5]:
                self.date['total_month'] += 1
            if date_p[3] != date_c[3]:
                self.date['total_day'] += 1
        if self.date['total_minutes'] != len(self._date) - 1:
            self.time = "Tick"
        else:
            self.time = "1M"

    def check_time_before_closing(self):
        for idx in range(self.current_step['step'] + 1 , len(self._date) - 1):
            if self._date[idx - 1][7] != self._date[idx][7]:
                break
        self.step_left = idx - self.current_step['step'] + 1


    def manage_date(self):
        self.day_changed = False
        if self.current_step['step'] > 0:
            if self._date[self.current_step['step'] - 1][3] != self._date[self.current_step['step']][3]:
                self.date['year'] += 1
                self.date['month'] = 1
                self.date['day'] = 1
                self.day_changed = True
            elif self._date[self.current_step['step'] - 1][5] != self._date[self.current_step['step']][5]:
                self.date['month'] += 1
                self.date['day'] = 1
                self.day_changed = True
            elif self._date[self.current_step['step'] - 1][7] != self._date[self.current_step['step']][7]:
                self.date['day'] += 1
                self.day_changed = True
        if self.day_changed is True:
            return 1
        else:
            return 0

    def get3DState(self):
        for idx in range(len(self.lst_data_preprocessed)):
            self.tensorOCHL[idx].append(self.lst_data_preprocessed[idx])
        state = getState(self.raw,
                         self.current_step['step'] + 1,
                         self.window_size + 1)
        d = self.current_step['step'] - self.window_size + 1
        #tensorState = [[] for _ in range(len(self.tensorOCHL))]
        tensorState = []
        for i in range(self.window_size):
            if d+i > 0 and i > 0:
                if self._date[self.current_step['step'] - (d + i)][11] == "0" or self._date[self.current_step['step'] - (d + i) + 1][11] == "5":
                    tensorState.append([state[i], state[i], state[i], state[i]])
                    #tensorState[1].append(state[i])
                    #tensorState[2].append(state[i])
                    #tensorState[3].append(state[i])
                elif self.current_step['step'] and self.tensorOCHL[2][self.current_step['step'] - (d + i)] > self.tensorOCHL[2][self.current_step['step'] - (d + i) + 1]:
                    tensorState.append([state[i], tensorState[i - 1][1], state[i], tensorState[i - 1][3]])
                    #tensorState[0].append(state[i])
                    #tensorState[1].append(tensorState[1][i - 1])
                    #tensorState[3].append(tensorState[3][i - 1])
                elif self.current_step['step'] and self.tensorOCHL[3][self.current_step['step'] - (d + i)] < self.tensorOCHL[3][self.current_step['step'] - (d + i) + 1]:
                    tensorState.append([state[i], tensorState[i - 1][1], tensorState[i - 1][2], state[i]])
                    #tensorState[3].append(state[i])
                    #tensorState[0].append(state[i])
                    #tensorState[1].append(tensorState[1][i - 1])
                    #tensorState[2].append(tensorState[2][i - 1])
                else:
                    tensorState.append([tensorState[i - 1][0], state[i], tensorState[i - 1][2], tensorState[i - 1][3]])
                    #tensorState[0].append(tensorState[0][i - 1])
                    #tensorState[3].append(tensorState[3][i - 1])
                    #tensorState[2].append(tensorState[2][i - 1])
                    #tensorState[1].append(state[i])
            else:
                tensorState.append([state[i], state[i], state[i], state[i]])
                #tensorState[0].append(state[i])
                #tensorState[1].append(state[i])
                #tensorState[2].append(state[i])
                #tensorState[3].append(state[i])

        return np.array(tensorState)

    def chart_preprocessing(self, data):
        if self.current_step['step'] == 0:
            self.lst_data_preprocessed = [data, data, data, data]
            self.lst_data_full.append((0,
                                       self.lst_data_preprocessed[0], #open
                                       self.lst_data_preprocessed[1], #close
                                       self.lst_data_preprocessed[2], #min
                                       self.lst_data_preprocessed[3], #high
                                       self.lst_act[len(self.lst_act) - 1]))

        #toutes les 5 ou 1 M ajouter nouvelle entrer dans la liste
        #modifier la liste dans cet interval
        if self.time == "Tick":
            #Passage en 1M
            if self.current_step['step'] > 0 and self._date[self.current_step['step'] - 1][11] != self._date[self.current_step['step']][11]:
                self.lst_data_preprocessed = [data, data, data, data]
                self.lst_data_full.append((int(self.current_step['step'] - self.offset),
                                           self.lst_data_preprocessed[0], #open
                                           self.lst_data_preprocessed[1], #close
                                           self.lst_data_preprocessed[2], #min
                                           self.lst_data_preprocessed[3], #high
                                           self.lst_act[len(self.lst_act) - 1]))
            else:
                if self.current_step['step'] > 0:
                    self.offset += 1
                if self.lst_data_preprocessed[2] > data:
                    self.lst_data_preprocessed[2] = data
                if self.lst_data_preprocessed[3] < data:
                    self.lst_data_preprocessed[3] = data
                self.lst_data_preprocessed[1] = data
                self.lst_data_full[len(self.lst_data_full) - 1] = (int(self.current_step['step'] - self.offset),
                                           self.lst_data_preprocessed[0], #open
                                           self.lst_data_preprocessed[1], #close
                                           self.lst_data_preprocessed[2], #min
                                           self.lst_data_preprocessed[3], #high
                                           self.lst_act[len(self.lst_act) - 1])
        elif self.time == "1M":
            #Passage en 5M
            if self._date[self.current_step['step']][11] == "0" or self._date[self.current_step['step']][11] == "5":
                self.lst_data_preprocessed = [data, data, data, data]
                self.lst_data_full.append((int(self.current_step['step'] - self.offset),
                                           self.lst_data_preprocessed[0], #open
                                           self.lst_data_preprocessed[1], #close
                                           self.lst_data_preprocessed[2], #min
                                           self.lst_data_preprocessed[3], #high
                                           self.lst_act[len(self.lst_act) - 1]))
            else:
                if self.current_step['step'] > 0:
                    self.offset += 1
                if self.lst_data_preprocessed[2] > data:
                    self.lst_data_preprocessed[2] = data
                if self.lst_data_preprocessed[3] < data:
                    self.lst_data_preprocessed[3] = data
                self.lst_data_preprocessed[1] = data
                self.lst_data_full[len(self.lst_data_full) - 1] = (int(self.current_step['step'] - self.offset),
                                           self.lst_data_preprocessed[0], #open
                                           self.lst_data_preprocessed[1], #close
                                           self.lst_data_preprocessed[2], #min
                                           self.lst_data_preprocessed[3], #high
                                           self.lst_act[len(self.lst_act) - 1])

    def daily_processing(self, terminal):
        if self.manage_date() == 1 or terminal is True:
            self.lst_reward_daily.append(self.reward['daily'])
            self.wallet.episode_process(self.trade)
            '''
            self.logger._add("Daily reward : " + str(self.reward['daily']), self._name)
            self.logger._add("Daily average rewards : " + str(self.avg_reward(env.lst_reward, 0)), self._name)
            self.logger._add("Daily profit : " + str(self.wallet.profit['daily']), self._name)
            self.logger._add("Daily trade : " + str(self.daily_trade['loss'] + self.daily_trade['win'] + self.daily_trade['draw']), self._name)
            if self.daily_trade['win'] + self.daily_trade['loss'] > 1:
                self.logger._add("Daily W/L : " + str('{:.3f}'.format(self.daily_trade['win'] / (self.daily_trade['loss'] + self.daily_trade['win']))), self._name)
            else:
                self.logger._add("Daily W/L : " + str('{:.3f}'.format(self.daily_trade['win'] / 1)), self._name)
            '''
            if self.wallet.profit['daily'] > 0:
                '''
                self.logger._add("Saving training data with " +
                                str(self.wallet.profit['daily']) +
                                " daily profit", self._name)
                '''
                self.logger.save_training_data(self.train_in,
                                              self.train_out)
            self.daily_reset()

    def execute(self, action):
        self.current_step['step'] += 1
        self.action = action
        self.POS_BUY = -1
        self.POS_SELL = -1
        if self.step_left == 0:
            self.check_time_before_closing()
        self.step_left -= 1
        self.price['buy'] = self.data[self.current_step['step']] - (self.contract_settings['spread'] / 2)
        self.price['sell'] = self.data[self.current_step['step']] + (self.contract_settings['spread'] / 2)
        #self.lst_state.append(self.state[0])
        self.reward['current'] = 0
        self.wallet.profit['current'] = 0
        self.wallet.manage_exposure(self.contract_settings)
        stopped = self.inventory.stop_loss(self)
        if stopped == False:
            force_closing = self.inventory.trade_closing(self)
            if force_closing == False:
                self.inventory.inventory_managment(self)
            else:
                self.POS_SELL = 0
                if self.inventory.get_last_trade()['close']['pos'] == "SELL":
                    self.action = 2
                else:
                    self.action = 1
        else:
            if self.action == 1:
                self.POS_BUY = 0
                self.action = 2
            elif self.action == 2:
                self.POS_SELL = 0
                self.action = 1
        self.train_in.append(self.state)
        self.train_out.append(act_processing(self.action))
        self.wallet.profit['daily'] += self.wallet.profit['current']
        self.wallet.profit['total'] += self.wallet.profit['current']
        self.reward['daily'] += self.reward['current']
        self.reward['total'] += self.reward['current']
        self.lst_reward.append(self.reward['current'])
        self.def_act()
        self.wallet.manage_wallet(self.inventory.get_inventory(), self.price, self.contract_settings)
        if self.gui == 1:
            self.chart_preprocessing(self.data[self.current_step['step']])
        self.state = getState(
                            self.raw,
                            self.current_step['step'] + 1,
                            self.window_size + 1)
        self.wallet.daily_process()
        done = True if len(self.data) - 2 == self.current_step['step'] else False
        if self.wallet.risk_managment['current_max_pos'] < 1 or self.wallet.risk_managment['current_max_pos'] <= int(self.wallet.risk_managment['max_pos'] // 2):
            self.wallet.settings['capital'] = self.wallet.settings['saved_capital']
            done = True
        return self.state, done, self.reward['current']

    def avg_reward(self, reward, n):
        if n == 0:
            return np.average(np.array(reward))
        return np.average(np.array(reward[(len(reward) - 1) - n:]))

    def daily_reset(self):
        self.wallet.daily_reset()
        self.lst_reward = []

        self.daily_trade['win'] = 0
        self.daily_trade['loss'] = 0
        self.daily_trade['draw'] = 0
        self.daily_trade['total'] = 0
        self.price['buy'] = 0
        self.price['sell'] = 0
        self.reward['current'] = 0
        self.reward['daily'] = 0

        self.train_in = []
        self.train_out = []

    def reset(self):
        self.daily_reset()
        self.wallet.reset()
        self.inventory.reset()

        try:
            self.h_lst_reward.append(self.reward['total'])
            self.h_lst_profit.append(self.wallet.profit['total'])
            self.h_lst_win_order.append(self.trade['win'])
            self.h_lst_loose_order.append(self.trade['loss'])
            self.h_lst_draw_order.append(self.trade['draw'])
        except:
            self.h_lst_reward = []
            self.h_lst_profit = []
            self.h_lst_win_order = []
            self.h_lst_loose_order = []
            self.h_lst_draw_order = []

        self.tensorOCHL = [[] for _ in range(4)]
        self.lst_reward_daily = []
        self.lst_data_full = deque(maxlen=100)
        self.date['day'] = 1
        self.date['month'] = 1
        self.date['year'] = 1
        self.date['total_minutes'] = 1
        self.date['total_day'] = 1
        self.date['total_month'] = 1
        self.date['total_year'] = 1
        self.trade['win'] = 0
        self.trade['loss'] = 0
        self.trade['draw'] = 0
        self.trade['total'] = 0
        self.current_step['order'] = ""
        self.current_step['step'] = -1
        self.reward['total'] = 0
        self.new_episode = True
        self.state = getState(
                                self.raw,
                                0,
                                self.window_size + 1)
        self.current_step['episode'] += 1
        return self.state
