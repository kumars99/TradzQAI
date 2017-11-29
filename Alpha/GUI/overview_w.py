from ttkthemes import themed_tk as tk
import tkinter.ttk
from environnement import *
from GUI.interface import *

class overview_window():

    def __init__(self, root, env):
        self.base = root
        self.dday = 1
        self.agent_value_init(env)
        self.agent_inventory_init(env)
        self.agent_orders_init()
        self.data_init(env)

    def agent_inventory_init(self, env):
        self.inventory = ttk.LabelFrame(self.base, text="Agent inventory")
        self.inventory.pack(fill="both", expand="no", side=RIGHT)

        self.inv = StringVar()
        self.inv.set(str(env.inventory))

        ttk.Label(self.inventory, textvariable=self.inv).pack(anchor='n')

        self.agent_winrate(env)

    def agent_orders_init(self):
        self.order = ttk.LabelFrame(self.base, text="Agent orders")
        self.order.pack(fill=BOTH, expand="yes")

        self.ordr = pd.DataFrame(columns=['Orders'])

        self.ord = StringVar()
        self.ord.set("None")

        ttk.Label(self.order, textvariable=self.ord).pack()

    def data_init(self, env):
        self.da = ttk.LabelFrame(self.base, text="Data")
        self.da.pack(fill="both", expand="no", side=BOTTOM)

        self.day = StringVar()
        if env.data == None:
            env.data = 0
        self.day.set("Day : " + str(self.dday) + " / " + '{:.0f}'.format(env.data / 4680))

        self.d = StringVar()
        self.d.set("Current : " +str(0)+ " / " +str(0))

        self.perc = StringVar()
        self.perc.set('{:.2f}'.format(0) + " %")

        ttk.Label(self.da, textvariable=self.perc).pack()
        ttk.Label(self.da, textvariable=self.day).pack()
        ttk.Label(self.da, textvariable=self.d).pack()

    def agent_value_init(self, env):
        self.l = ttk.LabelFrame(self.base, text="Agent values")
        self.l.pack(side=LEFT, fill=Y)

        self.aa = StringVar()
        self.aa.set("Action : " + str(env.act))

        ttk.Label(self.l, textvariable=self.aa).pack()

        self.agent_env(env)
        self.agent_profit(env)
        self.agent_reward(env)

    def agent_winrate(self, env):
        self.wr = ttk.LabelFrame(self.inventory , text="Orders")
        self.wr.pack(fill=X, side=BOTTOM)

        self.ow = StringVar()
        self.ow.set("Win : " + str(env.win))

        self.ol = StringVar()
        self.ol.set("Loose : " + str(env.loose))

        self.aod = StringVar()
        self.aod.set("Avg daily : " + str((env.loose + env.win) / self.dday))

        self.opm = StringVar()
        if env.cdatai == 0:
            self.opm.set("Trade per minute : " + '{:.2f}'.format((env.loose + env.win) / (1 / 6)))
        else:
            self.opm.set("Trade per minute : " + '{:.2f}'.format((env.loose + env.win) / (env.cdatai / ((env.data / 20)/ 9))))

        self.ts = StringVar()
        if env.data is None:
            self.ts.set("Trade speed : " + "0" + " ms")
        else:
            self.ts.set("Trade speed : " + ':.2f'.format(1/((((env.loose + env.win) / ((env.data / 20) / 9)) /60) /100)) + " ms")

        self.to = StringVar()
        self.to.set("Total : " + str (env.loose + env.win))

        self.winrate = StringVar()
        if env.loose == 0:
            self.winrate.set ("Winrate : " + str(env.loose/1))
        else:
            self.winrate.set("Winrate : " + '{:.3f}'.format(env.win / (env.loose + env.win)))

        ttk.Label(self.wr, textvariable=self.ow).pack(anchor='w')
        ttk.Label(self.wr, textvariable=self.ol).pack(anchor='w')
        ttk.Label(self.wr, textvariable=self.to).pack(anchor='w')
        ttk.Label(self.wr, textvariable=self.aod).pack(anchor='w')
        ttk.Label(self.wr, textvariable=self.opm).pack(anchor='w')
        ttk.Label(self.wr, textvariable=self.ts).pack(anchor='w')
        ttk.Label(self.wr, textvariable=self.winrate).pack(anchor='w')

    def agent_profit(self, env):
        self.profit = ttk.LabelFrame(self.l, text="Profit")
        self.profit.pack(fill=X)

        self.p = StringVar()
        self.p.set("Current : " + str(env.profit))


        self.p = StringVar()
        self.p.set("Current : " + str(env.profit))

        self.op = StringVar()
        if (env.win + env.loose) == 0:
            self.op.set("Avg : " + '{:.2f}'.format(env.total_profit / 1))
        else:
            self.op.set("Avg : " + '{:.2f}'.format(env.total_profit / (env.win + env.loose_r)))

        self.adp = StringVar()
        if env.cdatai % 4680 == 0:
            self.adp.set("Avg daily : " + '{:.2f}'.format(env.total_profit / 1))
        else:
            self.adp.set("Avg daily : " + '{:.2f}'.format(env.total_profit / (env.cdatai % 4680 )))

        self.dailyp = 0

        self.dp = StringVar()
        self.dp.set("Daily : " + str(self.dailyp))

        self.tp = StringVar()
        self.tp.set("Total : " + str(env.total_profit))

        ttk.Label(self.profit, textvariable=self.p).pack(anchor='w')
        ttk.Label(self.profit, textvariable=self.op).pack(anchor='w')
        ttk.Label(self.profit, textvariable=self.adp).pack(anchor='w')
        ttk.Label(self.profit, textvariable=self.dp).pack(anchor='w')
        ttk.Label(self.profit, textvariable=self.tp).pack(anchor='w')

    def agent_reward(self, env):
        self.tot_reward = 0
        self.daily_reward = 0

        self.rew = ttk.LabelFrame(self.l, text="Reward")
        self.rew.pack(fill=X)

        self.r = StringVar()
        self.r.set("Current : " + str(env.reward))

        self.ar = StringVar()
        self.ar.set("Avg : " + '{:.2f}'.format(self.tot_reward / 1))

        self.adr = StringVar()
        self.adr.set("Avg daily : " + '{:.2f}'.format(self.daily_reward / self.dday))

        self.dr = StringVar()
        self.dr.set("Daily : " + str(self.daily_reward))

        self.tr = StringVar()
        self.tr.set("Total : " + str(self.tot_reward))

        ttk.Label(self.rew, textvariable=self.r).pack(anchor='w')
        ttk.Label(self.rew, textvariable=self.ar).pack(anchor='w')
        ttk.Label(self.rew, textvariable=self.adr).pack(anchor='w')
        ttk.Label(self.rew, textvariable=self.dr).pack(anchor='w')
        ttk.Label(self.rew, textvariable=self.tr).pack(anchor='w')

    def agent_env(self, env):
        self.en = ttk.LabelFrame(self.l, text="Environnement")
        self.en.pack(fill=X)

        self.mode = StringVar()
        self.mode.set("Mode : " + env.mode)

        self.model = StringVar()
        self.model.set("Model : " + env.stock_name)

        self.mo = StringVar()
        self.mo.set("Max order : " + str(env.max_order))

        self.cp = StringVar()
        self.cp.set("Contract price : " + str(env.contract_price))

        self.sp = StringVar()
        self.sp.set("Spread : " + str(env.spread))

        ttk.Label(self.en, textvariable=self.mode).pack(anchor='w')
        ttk.Label(self.en, textvariable=self.model).pack(anchor='w')
        ttk.Label(self.en, textvariable=self.mo).pack(anchor='w')
        ttk.Label(self.en, textvariable=self.cp).pack(anchor='w')
        ttk.Label(self.en, textvariable=self.sp).pack(anchor='w')

    def update_overview(self, env):

        '''
        Day mod
        '''

        if int(env.cdatai / (env.data / 20)) == self.dday:
            self.dday += 1
            self.dailyp = 0
            self.daily_reward = 0

        self.daily_reward += env.reward
        self.tot_reward += env.reward

        '''
        Agent values
        '''

        self.aa.set("Action : " + str(env.act))

        '''
        Inventory
        '''

        if len(env.inventory['Price']) < 1:
            env.inventory = "Empty inventory"
        self.inv.set(str(env.inventory))

        '''
        Orders done
        '''

        self.ord.set(str(np.array(self.ordr)))

        '''
        Orders
        '''

        if env.cdatai == 0:
            self.opm.set("Trade per minute : " + '{:.2f}'.format((env.loose + env.win) / (1 / 6)))
        else:
            self.opm.set("Trade per minute : " + '{:.2f}'.format((env.loose + env.win) / (env.cdatai / ((env.data / 20)/ 9))))
        self.ow.set("Win : " + str(env.win))
        self.ol.set("Loose : " + str(env.loose))
        if env.data is None:
            self.ts.set("Trade speed : " + "0" + " ms")
        else:
            try:
                self.ts.set("Trade speed : " + '{:.0f}'.format(1.0/(((((env.loose + env.win) / (env.cdatai / ((env.data / 20.0) / 9.0))) /60.0) /100.0))) + " ms")
            except:
                self.ts.set("Trade speed : " + "0" + " ms")
        self.aod.set("Avg daily : " + '{:.2f}'.format((env.loose + env.win) / self.dday))
        self.to.set("Total : " + str (env.loose + env.win))
        if env.loose == 0:
            self.winrate.set ("Winrate : " + str(env.loose/1))
        else:
            self.winrate.set("Winrate : " + '{:.3f}'.format(env.win / (env.loose + env.win)))

        '''
        Data
        '''

        self.day.set("Day : " + str(self.dday) + " / " + '{:.0f}'.format(env.data / (env.data / 20)))
        self.d.set("Current : " +str(env.cdatai)+ " / " +str(env.data))
        self.perc.set('{:.2f}'.format(float((env.cdatai * 100 ) / env.data)) + " %")

        '''
        Profit
        '''

        self.p.set("Current : " + str(env.profit))
        if (env.win + env.loose) == 0:
            self.op.set("Avg : " + '{:.2f}'.format(env.total_profit / 1))
            self.adp.set("Avg daily : " + '{:.2f}'.format((env.total_profit / ( 1 )) * self.dday))
        else:
            self.op.set("Avg : " + '{:.2f}'.format(env.total_profit / (env.win + env.loose)))
            self.adp.set("Avg daily : " + '{:.2f}'.format((env.total_profit / self.dday)))
        self.dailyp += env.profit
        self.dp.set("Daily : " + str(self.dailyp))
        self.tp.set("Total : " + str(env.total_profit))

        '''
        Reward
        '''

        self.r.set("Current : " + str(env.reward))
        if env.cdatai == 0:
            self.ar.set("Avg : " + '{:.2f}'.format(self.tot_reward / 1))
            self.adr.set("Avg daily : " + '{:.2f}'.format((self.tot_reward / 1 ) * self.dday))
        else:
            self.ar.set("Avg : " + '{:.2f}'.format(self.tot_reward / env.cdatai))
            self.adr.set("Avg daily : " + '{:.2f}'.format(self.tot_reward / self.dday))
        self.dr.set("Daily : " + str(self.daily_reward))
        self.tr.set("Total : " + str(self.tot_reward))
