from tkinter import *
import tkinter.ttk as ttk
import train
from threading import Thread
from tkinter.filedialog import *
from tkinter.messagebox import *
from environnement import *
import pandas as pd

env = environnement()
env.stock_name = "dax30_2017_09"

class interface(Frame):

    def __init__(self, window, **kwargs):
        self.name = "TradzQAI"
        self.version = "Alpha v0.1"

        window.title(self.name + " " + self.version)
        window.resizable(0, 0)
        Frame.__init__(self, window, **kwargs)
        self.pack(fill=BOTH)

        self.m = train_thread()
        self.m.daemon=True

        self.build_start_window()

    def manage_orders(self):
        if len(self.ordr['Orders']) > 40:
            self.ordr = (self.ordr.drop(0)).reset_index(drop=True)
        if env.POS_BUY > -1 or env.POS_SELL > -1:
            if "SELL" in env.corder:
                POS = env.POS_BUY
                c = env.sell_price
            elif "BUY" in env.corder:
                POS = env.POS_SELL
                c = env.buy_price
            if len(env.inventory['Price']) > 0:
                new = [str((env.inventory['POS']).iloc[POS]) + " : " + str(env.cd) + " -> " + str(env.corder) + " : " + str(c) + " | Profit : " + str(float(env.profit))]
                tmp = pd.DataFrame(new, columns = ['Orders'])
                self.ordr = self.ordr.append(tmp, ignore_index=True)

    def build_start_window(self):
        self.start = LabelFrame(self, text="Mode")
        self.start.pack()

        self.train = Button(self.start, text="Train", command=self.build_train_window)
        self.train.pack(side=TOP)
        self.eval = Button(self.start, text="Eval", command=self.build_eval_window)
        self.eval.pack(side=TOP)

    def build_train_window(self):
        self.start.destroy()
        window.geometry("1024x720")

        env.mode = "train"

        self.quit = Button(self, text="Quit", command=quit)
        self.quit.pack(side=RIGHT, fill=BOTH)
        self.run_ai = Button(self, text="Run", command=self.go_run)
        self.run_ai.pack(side=LEFT, fill=BOTH)
        self.parsing = Button(self, text="Pause", command=self.m.pause)
        self.parsing.pack(side=LEFT, fill=BOTH)
        self.but = Button(self, text="Resume", command=self.m.resume)
        self.but.pack(fill=BOTH, side=LEFT)

        self.dday = 1
        self.agent_value_init()
        self.agent_inventory_init()
        self.agent_orders_init()
        self.data_init()

    def build_eval_window(self):
        self.start.destroy()

        window.geometry("1024x720")

        env.mode = "eval"

        self.quit = Button(self, text="Quit", command=quit)
        self.quit.pack(side=RIGHT, fill=BOTH)
        self.run_ai = Button(self, text="Run", command=self.go_run)
        self.run_ai.pack(side=LEFT, fill=BOTH)
        self.parsing = Button(self, text="Pause", command=self.m.pause)
        self.parsing.pack(side=LEFT, fill=BOTH)
        self.but = Button(self, text="Resume", command=self.m.resume)
        self.but.pack(fill=BOTH, side=LEFT)
        
        self.dday = 1
        self.agent_value_init()
        self.agent_inventory_init()
        self.agent_orders_init()
        self.data_init()

    def agent_inventory_init(self):
        self.inventory = LabelFrame(window, text="Agent inventory", padx=2, pady=2)
        self.inventory.pack(fill="both", expand="no", side=RIGHT)

        self.inv = StringVar()
        self.inv.set(str(env.inventory))

        Label(self.inventory, textvariable=self.inv).pack(anchor='n')

        self.agent_winrate()


    def agent_orders_init(self):
        self.order = LabelFrame(window, text="Agent orders", padx=3, pady=4)
        self.order.pack(fill="both", expand="yes")

        self.ordr = pd.DataFrame(columns=['Orders'])

        self.ord = StringVar()
        self.ord.set("None")

        Label(self.order, textvariable=self.ord).pack()

    def data_init(self):
        self.da = LabelFrame(window, text="Data", padx=2, pady=0.5)
        self.da.pack(fill="both", expand="no", side=BOTTOM)

        self.day = StringVar()
        if env.data == None:
            env.data = 0
        self.day.set("Day : " + str(self.dday) + " / " + '{:.0f}'.format(env.data / 4680))

        self.d = StringVar()
        self.d.set("Current data : " +str(0)+ " / " +str(0))

        Label(self.da, textvariable=self.day).pack()
        Label(self.da, textvariable=self.d).pack()


    def agent_value_init(self):
        self.l = LabelFrame(window, text="Agent values", padx=2, pady=2)
        self.l.pack(side=LEFT, fill=Y)

        self.aa = StringVar()
        self.aa.set("Action : " + str(env.act))

        Label(self.l, textvariable=self.aa).pack()

        self.agent_env()
        self.agent_profit()
        self.agent_reward()


    def agent_winrate(self):
        self.wr = LabelFrame(self.inventory , text="Orders", padx=2, pady=2)
        self.wr.pack(fill=X, side=BOTTOM)

        self.ow = StringVar()
        self.ow.set("Win : " + str(env.win))

        self.ol = StringVar()
        self.ol.set("Loose : " + str(env.loose_r))

        self.aod = StringVar()
        self.aod.set("Avg daily : " + str((env.loose_r + env.win) / self.dday))

        self.opm = StringVar()
        if env.cdatai == 0:
            self.opm.set("Trade per minute : " + '{:.2f}'.format((env.loose_r + env.win) / (1 / 6)))
        else:
            self.opm.set("Trade per minute : " + '{:.2f}'.format((env.loose_r + env.win) / (env.cdatai / ((env.data / 20)/ 9))))

        self.ts = StringVar()
        if env.data is None:
            self.ts.set("Trade speed : " + "0" + " ms")
        else:
            self.ts.set("Trade speed : " + ':.2f'.format(1/((((env.loose_r + env.win) / ((env.data / 20) / 9)) /60) /100)) + " ms")

        self.to = StringVar()
        self.to.set("Total : " + str (env.loose_r + env.win))

        self.winrate = StringVar()
        if env.loose_r== 0:
            self.winrate.set ("Winrate : " + str(env.loose_r/1))
        else:
            self.winrate.set("Winrate : " + '{:.3f}'.format(env.win / (env.loose_r + env.win)))

        Label(self.wr, textvariable=self.ow).pack(anchor='w')
        Label(self.wr, textvariable=self.ol).pack(anchor='w')
        Label(self.wr, textvariable=self.to).pack(anchor='w')
        Label(self.wr, textvariable=self.aod).pack(anchor='w')
        Label(self.wr, textvariable=self.opm).pack(anchor='w')
        Label(self.wr, textvariable=self.ts).pack(anchor='w')
        Label(self.wr, textvariable=self.winrate).pack(anchor='w')

    def agent_profit(self):
        self.profit = LabelFrame(self.l, text="Profit", padx=2, pady=2)
        self.profit.pack(fill=X)

        self.p = StringVar()
        self.p.set("Current : " + str(env.profit))

        self.op = StringVar()
        if (env.win + env.loose_r) == 0:
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

        Label(self.profit, textvariable=self.p).pack(anchor='w')
        Label(self.profit, textvariable=self.op).pack(anchor='w')
        Label(self.profit, textvariable=self.adp).pack(anchor='w')
        Label(self.profit, textvariable=self.dp).pack(anchor='w')
        Label(self.profit, textvariable=self.tp).pack(anchor='w')

    def agent_reward(self):
        self.tot_reward = 0
        self.daily_reward = 0

        self.rew = LabelFrame(self.l, text="Reward", padx=2, pady=2)
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

        Label(self.rew, textvariable=self.r).pack(anchor='w')
        Label(self.rew, textvariable=self.ar).pack(anchor='w')
        Label(self.rew, textvariable=self.adr).pack(anchor='w')
        Label(self.rew, textvariable=self.dr).pack(anchor='w')
        Label(self.rew, textvariable=self.tr).pack(anchor='w')

    def agent_env(self):
        self.en = LabelFrame(self.l, text="Environnement", padx=2, pady=2)
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

        Label(self.en, textvariable=self.mode).pack(anchor='w')
        Label(self.en, textvariable=self.model).pack(anchor='w')
        Label(self.en, textvariable=self.mo).pack(anchor='w')
        Label(self.en, textvariable=self.cp).pack(anchor='w')
        Label(self.en, textvariable=self.sp).pack(anchor='w')

    def go_run(self):
        self.m.start()

    def text_update(self, state):
        self.text.insert(END, "\n")
        self.text.insert(END, state)
        self.pack()

    def update(self):
        self.manage_orders()

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

        self.ord.set(str(self.ordr))

        '''
        Orders
        '''

        if env.cdatai == 0:
            self.opm.set("Trade per minute : " + '{:.2f}'.format((env.loose_r + env.win) / (1 / 6)))
        else:
            self.opm.set("Trade per minute : " + '{:.2f}'.format((env.loose_r + env.win) / (env.cdatai / ((env.data / 20)/ 9))))
        self.ow.set("Win : " + str(env.win))
        self.ol.set("Loose : " + str(env.loose_r))
        if env.data is None:
            self.ts.set("Trade speed : " + "0" + " ms")
        else:
            try:
                self.ts.set("Trade speed : " + '{:.0f}'.format(1.0/(((((env.loose_r + env.win) / (env.cdatai / ((env.data / 20.0) / 9.0))) /60.0) /100.0))) + " ms")
            except:
                self.ts.set("Trade speed : " + "0" + " ms")
        self.aod.set("Avg daily : " + '{:.2f}'.format((env.loose_r + env.win) / self.dday))
        self.to.set("Total : " + str (env.loose_r + env.win))
        if env.loose_r == 0:
            self.winrate.set ("Winrate : " + str(env.loose_r/1))
        else:
            self.winrate.set("Winrate : " + '{:.3f}'.format(env.win / (env.loose_r + env.win)))

        '''
        Data
        '''

        self.day.set("Day : " + str(self.dday) + " / " + '{:.0f}'.format(env.data / (env.data / 20)))
        self.d.set("Current : " +str(env.cdatai)+ " / " +str(env.data))

        '''
        Profit
        '''

        self.p.set("Current : " + str(env.profit))
        if (env.win + env.loose_r) == 0:
            self.op.set("Avg : " + '{:.2f}'.format(env.total_profit / 1))
            self.adp.set("Avg daily : " + '{:.2f}'.format((env.total_profit / ( 1 )) * self.dday))
        else:
            self.op.set("Avg : " + '{:.2f}'.format(env.total_profit / (env.win + env.loose_r)))
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

        self.l.update_idletasks()

class train_thread(Thread):

    def __init__(self):
        Thread.__init__(self)

    def pause(self):
        self.t.b = 1

    def resume(self):
        self.t.b = 0

    def run(self):
        self.t = train.train(env, interfaces)
        self.t.training()


def launch_interface():
    interfaces.mainloop()


window = Tk()
interfaces = interface(window)
