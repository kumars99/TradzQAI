from tkinter import *
import tkinter.ttk as ttk
import train
from threading import Thread
from tkinter.filedialog import *
from tkinter.messagebox import *
from environnement import *
import pandas as pd

env = environnement()
env.stock_name = "DAX30_2011_01"

class interface(Frame):

    def __init__(self, window, **kwargs):
        self.name = "TradzQAI"
        self.version = "Alpha v0.1"
        window.title(self.name + " " + self.version)
        window.resizable(0, 0)
        window.geometry("1024x720")
        self.m = my_thread()
        self.m.daemon=True
        Frame.__init__(self, window, **kwargs)
        self.pack(fill=BOTH)
        self.text = Text(window, width=100, height=100)
        self.text.insert(INSERT, self.name + " " + self.version)

        self.l = LabelFrame(window, text="Agent values", padx=2, pady=2)
        self.l.pack(fill="both", expand="no", side=LEFT)

        self.inventory = LabelFrame(window, text="Agent inventory", padx=2, pady=2)
        self.inventory.pack(fill="both", expand="no", side=RIGHT)

        self.order = LabelFrame(window, text="Agent trade", padx=2, pady=2)
        self.order.pack(fill="both", expand="no")

        self.ordr = pd.DataFrame(columns=['Orders'])
        self.init_label()
        '''
        self.w = PanedWindow(window, orient=HORIZONTAL)
        self.w.pack(side=TOP, pady=2, padx=2)
        self.w.pack()
        '''
        self.parsing = Button(self, text="Pause", command=self.m.p)
        self.parsing.pack(side=RIGHT, fill=BOTH)
        self.but = Button(self, text="Resume", command=self.m.r)
        self.but.pack(fill=BOTH, side=RIGHT)
        self.run_ai = Button(self, text="Run", command=self.go_run)
        self.run_ai.pack(side=RIGHT, fill=BOTH)

    def manage_orders(self):
        if len(self.ordr['Orders']) > 30:
            self.ordr = (self.ordr.drop(0)).reset_index(drop=True)
        if env.POS_BUY > -1 or env.POS_SELL > -1:
            if len(env.inventory['Price']) > 0:
                new = ["Close : " + str(env.cdata) + " -> " + str(env.corder) + " : " + str((env.inventory['Price']).iloc[0])]
                tmp = pd.DataFrame(new, columns = ['Orders'])
                self.ordr = self.ordr.append(tmp, ignore_index=True)

    def init_ltxt(self):
        self.manage_orders()

        self.p = StringVar()
        self.p.set("Profit : " + str(env.profit))

        self.tp = StringVar()
        self.tp.set("Total profit : " + str(env.total_profit))

        self.r = StringVar()
        self.r.set("Current reward : " + str(env.reward))

        self.o = StringVar()
        self.o.set("Order type : " + str(env.corder))

        self.inv = StringVar()
        self.inv.set(str(env.inventory))

        self.ord = StringVar()
        self.ord.set("None")

    def init_label(self):
        self.init_ltxt()
        Label(self.l, textvariable=self.o).pack()
        Label(self.l, textvariable=self.r).pack()
        Label(self.l, textvariable=self.p).pack()
        Label(self.l, textvariable=self.tp).pack()
        Label(self.inventory, textvariable=self.inv).pack()
        Label(self.order, textvariable=self.ord).pack()
        

    def go_run(self):
        self.m.start()
        #self.update()

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
        self.inv.set(str(env.inventory))
        self.ord.set(str(self.ordr))
        self.l.update_idletasks()

class my_thread(Thread):

    def __init__(self):
        Thread.__init__(self)

    def p(self):
        self.t.b = 1

    def r(self):
        self.t.b = 0

    def run(self):
        self.t = train.train(env, interfaces)
        self.t.training()


def launch_interface():
    interfaces.mainloop()


window = Tk()
interfaces = interface(window)
