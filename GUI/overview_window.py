from environnement import Environnement
from tools import *

import time

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import pandas as pd
import numpy as np

class Overview_Window(QWidget):

    def __init__(self, root, env):
        super(QWidget, self).__init__(root)

        self.ordr = pd.DataFrame(columns=['Orders'])
        self.dailyp = 0
        self.daily_reward = 0
        self.tot_reward = 0
        self.dday = 1
        self.lt = 0

        GB = QGridLayout(self)

        GB.addWidget(self.Agent_Inventory_Init(), 0, 2, 2, 1)
        GB.addWidget(self.Agent_Orders_Init(), 0, 1)
        GB.addWidget(self.Agent_Value_Init(env), 0, 0, 2, 1)
        GB.addWidget(self.Data_Init(), 1, 1)

    def Agent_env(self, env):

        GBox = QGroupBox("Environnement")
        VBox = QVBoxLayout()

        self.lmode = QLabel('Mode : ' + env.mode)
        self.lmodel = QLabel('Model : ' + env.stock_name)
        self.lmax_order = QLabel('Max pos : ' + str(env.max_pos))
        self.lcontract_price = QLabel('Contract price : ' + str(env.contract_price))
        self.lpip_value = QLabel('Pip Value : ' + str(env.pip_value))
        self.lspread = QLabel('Spread : ' + str(env.spread))

        VBox.addWidget(self.lmode)
        VBox.addWidget(self.lmodel)
        VBox.addWidget(self.lmax_order)
        VBox.addWidget(self.lcontract_price)
        VBox.addWidget(self.lpip_value)
        VBox.addWidget(self.lspread)

        VBox.addStretch(1)

        GBox.setLayout(VBox)
        GBox.setFixedSize(220,180)
        return GBox

    def Agent_Inventory_Init(self):

        GBox = QGroupBox("Agent inventory")
        VBox = QVBoxLayout()

        self.linventory = QLabel('Empty inventory')

        self.linventory.setAlignment(Qt.AlignHCenter)

        VBox.addWidget(self.linventory)
        VBox.addWidget(self.Agent_Winrate())

        #VBox.addStretch()

        GBox.setLayout(VBox)
        GBox.setFixedSize(245,915)

        return GBox

    def Agent_Orders_Init(self):

        GBox = QGroupBox("Agent orders")
        VBox = QVBoxLayout()

        self.lorder = QLabel('No orders taken yet')

        self.lorder.setAlignment(Qt.AlignCenter)

        VBox.addWidget(self.lorder)

        VBox.addStretch()

        GBox.setLayout(VBox)
        GBox.setFixedSize(1250,775)

        return GBox

    def Data_Init(self):

        GBox = QGroupBox("Data")
        VBox = QVBoxLayout()

        self.lday = QLabel('Day : 0 / 0')
        self.lperc = QLabel('0 %')
        self.ldata = QLabel('Data : 0 / 0')

        self.lperc.setAlignment(Qt.AlignCenter)
        self.lday.setAlignment(Qt.AlignCenter)
        self.ldata.setAlignment(Qt.AlignCenter)

        VBox.addWidget(self.lperc)
        VBox.addWidget(self.lday)
        VBox.addWidget(self.ldata)

        VBox.addStretch()

        GBox.setLayout(VBox)
        GBox.setFixedSize(1250,115)
        GBox.setAlignment(Qt.AlignCenter)

        return GBox

    def Agent_Winrate(self):

        GBox = QGroupBox("Winrate")
        VBox = QVBoxLayout()

        self.lwin = QLabel('Win : 0')
        self.lloose = QLabel('Loose : 0')
        self.ldraw = QLabel('Draw : 0')
        self.ltoto = QLabel('Total : 0')
        self.lwinrate = QLabel('Winrate : 0')

        VBox.addWidget(self.lwin)
        VBox.addWidget(self.lloose)
        VBox.addWidget(self.ldraw)
        VBox.addWidget(self.ltoto)
        VBox.addWidget(self.lwinrate)

        VBox.addStretch()

        GBox.setLayout(VBox)
        GBox.setFixedSize(220,155)

        return GBox

    def Agent_Value_Init(self, env):

        GBox = QGroupBox("Agent value")
        VBox = QVBoxLayout()

        self.lact = QLabel('Action : None')

        self.lact.setAlignment(Qt.AlignHCenter)

        VBox.addWidget(self.lact)
        VBox.addWidget(self.Agent_env(env))
        VBox.addWidget(self.Agent_Wallet(env))
        VBox.addWidget(self.Agent_Profit())
        VBox.addWidget(self.Agent_Reward())
        VBox.addWidget(self.Time_Init())

        VBox.addStretch()

        GBox.setLayout(VBox)
        GBox.setFixedSize(245,915)

        return GBox

    def Agent_Wallet(self, env):

        GBox = QGroupBox("Wallet")
        VBox = QVBoxLayout()

        self.lcap = QLabel('Capital : ' + formatPrice(env.capital))
        self.lcgl = QLabel('Current G/L : ' + formatPrice(env.cgl))
        self.lusable_margin = QLabel('Usable margin : ' + formatPrice(env.usable_margin))
        self.lused_margin = QLabel('Used margin : ' + formatPrice(env.used_margin))

        VBox.addWidget(self.lcap)
        VBox.addWidget(self.lcgl)
        VBox.addWidget(self.lusable_margin)
        VBox.addWidget(self.lused_margin)

        VBox.addStretch()

        GBox.setLayout(VBox)
        GBox.setFixedSize(220,130)

        return GBox

    def Agent_Profit(self):

        GBox = QGroupBox("Profit")
        VBox = QVBoxLayout()

        self.lcurp = QLabel('Current : 0')
        self.ldailyp = QLabel('Daily : 0')
        self.ltotp = QLabel('Total : 0')

        VBox.addWidget(self.lcurp)
        VBox.addWidget(self.ldailyp)
        VBox.addWidget(self.ltotp)

        VBox.addStretch()

        GBox.setLayout(VBox)
        GBox.setFixedSize(220,100)

        return GBox

    def Agent_Reward(self):

        GBox = QGroupBox("Reward")
        VBox = QVBoxLayout()

        self.lcurr = QLabel('Current : 0')
        self.ldailyr = QLabel('Daily : 0')
        self.ltotr = QLabel('Total : 0')

        VBox.addWidget(self.lcurr)
        VBox.addWidget(self.ldailyr)
        VBox.addWidget(self.ltotr)

        VBox.addStretch()

        GBox.setLayout(VBox)
        GBox.setFixedSize(220,100)

        return GBox

    def Time_Init(self):

        GBox = QGroupBox("Time")
        VBox = QVBoxLayout()

        self.lstart_t = QLabel('Since start : ' + time.strftime("%H:%M:%S", time.gmtime(0)))
        self.lloop_t = QLabel('Loop : 0 ms')
        self.leta = QLabel('ETA : ' + time.strftime("%H:%M:%S", time.gmtime(0)))
        
        VBox.addWidget(self.lstart_t)
        VBox.addWidget(self.lloop_t)
        VBox.addWidget(self.leta)

        VBox.addStretch()

        GBox.setLayout(VBox)
        GBox.setFixedSize(220,100)

        return GBox

    def Update_Overview(self, env):
        #Day mod

        # Daily reset
        if int(env.cdatai / (env.data / 20)) == self.dday:
            self.dday += 1
            self.dailyp = 0
            self.daily_reward = 0

        # Episode reset
        if env.cdatai == env.data - 1:
            self.dday = 1
            self.dailyp = 0
            self.daily_reward = 0
            self.tot_reward = 0
            self.lt = 0

        self.daily_reward += env.reward
        self.tot_reward += env.reward
        self.dailyp += env.profit


        #Agent Values

        self.lact.setText('Action : ' + str(env.act))

        #Inventory

        if not 'Empty inventory' in env.inventory and len(env.inventory['Price']) < 1:
            env.inventory = 'Empty inventory'
        self.linventory.setText(str(env.inventory))

        #Orders Done

        self.lorder.setText(str(np.array(self.ordr)))

        #Orders

        
        self.lwin.setText("Win : " + str(env.win))
        self.lloose.setText("Loose : " + str(env.loose))
        self.ldraw.setText("Draw : " + str(env.draw))
        self.ltoto.setText("Total : " + str (env.loose + env.win + env.draw))
        if env.loose == 0:
            self.lwinrate.setText("Winrate : " + str(1))
        else:
            self.lwinrate.setText("Winrate : " + '{:.3f}'.format(env.win / (env.loose + env.win)))

        #Data

        self.lday.setText("Day : " + str(self.dday) + " / " + '{:.0f}'.format(env.data / (env.data / 20)))
        self.ldata.setText("Current : " +str(env.cdatai)+ " / " +str(env.data))
        self.lperc.setText('{:.2f}'.format(float((env.cdatai * 100 ) / env.data)) + " %")

        #Wallet

        self.lcap.setText('Capital : ' + formatPrice(env.capital))
        self.lcgl.setText('Current G/L : ' + formatPrice(env.cgl))
        self.lusable_margin.setText('Usable margin : ' + formatPrice(env.usable_margin))
        self.lused_margin.setText('Used margin : ' + formatPrice(env.used_margin))

        #Profit

        self.lcurp.setText("Current : " + formatPrice(env.profit))
        self.ldailyp.setText("Daily : " + formatPrice(self.dailyp))
        self.ltotp.setText("Total : " + formatPrice(env.total_profit))

        #Reward

        self.lcurr.setText("Current : " + str(env.reward))
        self.ldailyr.setText("Daily : " + str(self.daily_reward))
        self.ltotr.setText("Total : " + str(self.tot_reward))

        #Time

        now = time.time() - env.start_t
        self.lstart_t.setText("Since start : " + '{:3d}'.format(int(time.strftime("%d", time.gmtime(now))) - 1) + ":" + time.strftime("%H:%M:%S", time.gmtime(now)))
        self.lloop_t.setText("Loop : " + str(round((env.loop_t * 100), 3)) + " ms")

        if env.cdatai > 0 :
            self.lt += env.loop_t
            self.leta.setText("ETA : " + '{:3d}'.format(int(time.strftime("%d", time.gmtime(((self.lt / env.cdatai ) * (env.data - env.cdatai))))) - 1) + ":" + time.strftime("%H:%M:%S", time.gmtime((self.lt / env.cdatai) * (env.data - env.cdatai))))
        else:
            self.leta.setText("ETA : " + '{:3d}'.format(int(time.strftime("%d", time.gmtime((self.lt / 1 ) * (env.data)))) - 1) + ":" + time.strftime("%H:%M:%S", time.gmtime((self.lt / 1) * (env.data))))
