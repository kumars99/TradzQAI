from tools.logger import *

class environnement():

    def __init__(self):

        # Environnement settings

        self.mode = ""
        self.stock_name = "dax30_2017_10_1M"
        self.episode_count = 100
        self.window_size = 100
        self.batch_size = 32

        # Wallet settings

        self.spread = 1
        self.max_order = 20
        self.pip_value = 5
        self.contract_price = 125

        # Wallet state

        self.wallet = 10000
        self.drawdown = 0
        self._return = 0
        self.max_return = 0
        self.max_drawdown = 0

        # Agent state

        self.total_profit = 0
        self.reward = 0
        self.profit = 0
        self.pause = 0
        self.inventory = None
        self.act = ""

        # DQN env helper

        self.data = None
        self.buy_price = 0
        self.sell_price = 0
        self.POS_BUY = -1
        self.POS_SELL = -1

        # Current data and order dropped from inventory

        self.cd = 0 
        self.co = ""

        # Current data and order from loop

        self.corder = ""
        self.cdata = 0
        self.cdatai = 0

        # orders

        self.win = 0
        self.loose = 0
        self.draw = 0

        # Time

        self.start_t = 0
        self.loop_t = 0

        # List for graph building

        ## Daily list

        ### Overview list

        self.lst_data = []
        self.lst_inventory_len = []
        self.lst_profit = []
        self.lst_win_order = []
        self.lst_loose_order = []
        self.lst_draw_order = []

        ### Model list

        self.lst_act = []
        self.lst_reward = []
        self.lst_act_predit = []
        self.lst_traget_predict = []
        self.lst_target = []
        self.lst_state = []
        self.lst_epsilon = []

        ## Episode list

        ### Historical list

        self.h_lst_reward = []
        self.h_lst_profit = []
        self.h_lst_win_order = []
        self.h_lst_loose_order = []
        self.h_lst_draw_order = []

        # Init logger

        #self.logs = logger(self)

    def def_act(self, act):
        if act == 1:
            self.act = "BUY"
            self.lst_act.append(1)
        elif act == 2:
            self.act = "SELL"
            self.lst_act.append(-1)
        else:
            self.act = "HOLD"
            self.lst_act.append(0)

    def _pause(self):
        self.pause = 1

    def _resume(self):
        self.pause = 0
