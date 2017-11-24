from tkinter import *
import tkinter.ttk as ttk
import train
from threading import Thread
from tkinter.filedialog import *
from tkinter.messagebox import *
from environnement import *
import pandas as pd

env = environnement()
env.stock_name = "DAX30_2011_01_10s"

class interface(Frame):

    def __init__(self, window, **kwargs):
        self.name = "TradzQAI"
        self.version = "Alpha v0.1"

        window.title(self.name + " " + self.version)
        window.resizable(0, 0)
        window.geometry("1024x720")
        Frame.__init__(self, window, **kwargs)
        self.pack(fill=BOTH)

        self.m = train_thread()
        self.m.daemon=True

        self.build_train_window()

        self.quit = Button(self, text="Quit", command=quit)
        self.quit.pack(side=RIGHT, fill=BOTH)
        self.run_ai = Button(self, text="Run", command=self.go_run)
        self.run_ai.pack(side=LEFT, fill=BOTH)
        self.parsing = Button(self, text="Pause", command=self.m.pause)
        self.parsing.pack(side=LEFT, fill=BOTH)
        self.but = Button(self, text="Resume", command=self.m.resume)
        self.but.pack(fill=BOTH, side=LEFT)

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
                new = [str((env.inventory['POS']).iloc[POS]) + " : " + str(env.cd) + " -> " + str(env.corder) + " : " + str(c) + " | Profit : " + str(env.profit)]
                tmp = pd.DataFrame(new, columns = ['Orders'])
                self.ordr = self.ordr.append(tmp, ignore_index=True)

    def build_train_window(self):
        self.agent_value_init()
        self.agent_inventory_init()
        self.agent_orders_init()
        self.data_init()

    def agent_inventory_init(self):
        self.inventory = LabelFrame(window, text="Agent inventory", padx=2, pady=2)
        self.inventory.pack(fill="both", expand="no", side=RIGHT)

        self.inv = StringVar()
        self.inv.set(str(env.inventory))

        Label(self.inventory, textvariable=self.inv).pack()


    def agent_orders_init(self):
        self.order = LabelFrame(window, text="Agent trade", padx=3, pady=4)
        self.order.pack(fill="both", expand="yes")

        self.ordr = pd.DataFrame(columns=['Orders'])

        self.ord = StringVar()
        self.ord.set("None")

        Label(self.order, textvariable=self.ord).pack()

    def data_init(self):
        self.da = LabelFrame(window, text="Data", padx=2, pady=0.5)
        self.da.pack(fill="both", expand="no", side=BOTTOM)

        self.d = StringVar()
        self.d.set("Current data : " +str(env.cdatai)+ " / " +str(env.data))

        Label(self.da, textvariable=self.d).pack()


    def agent_value_init(self):
        self.l = LabelFrame(window, text="Agent values", padx=2, pady=2)
        self.l.pack(side=LEFT, fill=Y)

        self.p = StringVar()
        self.p.set("Profit : " + str(env.profit))

        self.tp = StringVar()
        self.tp.set("Total profit : " + str(env.total_profit))

        self.r = StringVar()
        self.r.set("Current reward : " + str(env.reward))

        self.o = StringVar()
        self.o.set("Order type : " + str(env.corder))

        Label(self.l, textvariable=self.o).pack()
        Label(self.l, textvariable=self.r).pack()
        Label(self.l, textvariable=self.p).pack()
        Label(self.l, textvariable=self.tp).pack()

    def go_run(self):
        self.m.start()

    def text_update(self, state):
        self.text.insert(END, "\n")
        self.text.insert(END, state)
        self.pack()

    def update(self):
        self.manage_orders()
        self.p.set("Profit : " + str(env.profit))
        self.tp.set("Total profit : " + str(env.total_profit))
        self.r.set("Current reward : " + str(env.reward))
        self.o.set("Order type : " + str(env.corder))
        if len(env.inventory['Price']) < 1:
            env.inventory = "Empty inventory"
        self.inv.set(str(env.inventory))
        self.ord.set(str(self.ordr))
        self.d.set("Current data : " +str(env.cdatai)+ " / " +str(env.data))
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
