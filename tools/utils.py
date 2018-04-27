import numpy as np
import pandas as pd

import time
import os
import math

from tools.indicators import indicators


def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

#### Data managment ####

# Getting data

def open_row(files):
    #files = "./dataset/"+"EUR_USD"+time.strftime("_%d_%m_%y")+".csv"
    names = ['Time', 'Open', 'High', 'Low', 'Close', '']
    print ("Opening : %s" % files)
    #indics = indicators()
    csv = pd.read_csv(files, names=names, header = 0, sep=';')
    csv.drop(csv.columns[[5]], axis = 1, inplace = True)
    #csv = csv.join(indics.build_indicators(csv['Close']))
    return csv

# Get all data

def get_all_data(path):
    # list path directoy
    names = ['Time', 'Open', 'High', 'Low', 'Close', '']
    dirs = os.listdir(path)
    data = None
    dirs.sort()
    for d in dirs:
        # list files in directoy
        n = str(path)+"/"+str(d)
        files = os.listdir(n)
        for f in files:
            # check if file is csv
            if ".csv" in f:
                n = str(path)+"/"+str(d)+"/"+str(f)
                print ("Opening :", n)
                # Opening csv file
                csv = pd.read_csv(n, names=names, header = 0, error_bad_lines=False, sep=';')
                csv.drop(csv.columns[[1, 2, 3, 5]], axis = 1, inplace = True)
                if data is None:
                    data = csv
                else:
                    data = data.append(csv, ignore_index=True)
    indics = indicators()
    data = data.join(indics.build_indicators(data['Close']))
    print ("All files opened")
    return data

# Change tick to 10s

def open_tick(path):#, name, date):
    names = ['Time', 'BID', 'ASK', 'Volume']
    #indics = indicators()
    print ("Opening : %s" % path)
    tick = pd.read_csv(path, names=names, header = 0, error_bad_lines=False, sep=',')
    tick.drop(tick.columns[[2, 3]], axis = 1, inplace = True)
    #tick = tick.join(indics.build_indicators(tick['BID']))
    #path = path.replace(name, date+".csv")
    #tick.to_csv(path, sep = ';', mode = 'w')

    return tick

def build_10s(path):
    tick = open_tick(path)
    hi = []
    lo = []
    op = []
    cl = []
    t = []
    i = 0
    o = tick['BID'][i]
    h = o
    l = o
    while i <len(tick['BID']) - 1:
        if float(h) < float(tick['BID'][i]):
            h = tick['BID'][i]
        if float(l) > float(tick['BID'][i]):
            l = tick['BID'][i]
        if tick['Time'][i][13] != tick['Time'][i + 1][13]:
            if ((int(tick['Time'][i][13]) + 1) % 6) != int(tick['Time'][i + 1][13]):
                ti = tick['Time'][i]
                n = int(tick['Time'][i][13])
                while n != int(tick['Time'][i + 1][13]):
                    n = (n + 1) % 6
                    ti = ti[:13] + str(n) + ti[14:]
                    cl.append(tick['BID'][i])
                    op.append(o)
                    hi.append(h)
                    lo.append(l)
                    t.append(ti)
            else:
                cl.append(tick['BID'][i])
                op.append(o)
                hi.append(h)
                lo.append(l)
                t.append(tick['Time'][i])
            o = tick['BID'][i + 1]
            h = o
            l = o
        i += 1
    t = pd.DataFrame(t, columns=['Time'])
    low = pd.DataFrame(lo, columns=['Low'])
    high = pd.DataFrame(hi, columns=['High'])
    close = pd.DataFrame(cl, columns=['Close'])
    opening = pd.DataFrame(op, columns=['Open'])
    ret = t.join(opening)
    ret = ret.join(high)
    ret = ret.join(low)
    ret = ret.join(close)
    return ret


def save_10s(path, stock):
    stock.to_csv(path, sep = ';', mode = 'w')
    print ("Data saved in %s" % path)

def load_10s(path):
    names = ['Time', 'Open', 'High', 'Low', 'Close']
    stock = pd.read_csv(path, names=names, header = 0, error_bad_lines=False, sep=';')
    print ("Data loaded from %s" % path)
    return stock

def check_10s(path, f):
    #indics = indicators()
    tick_path = "./dataset/DAX30/10S"
    name = (path.replace("./dataset/DAX30/Tick", "")).replace(f, "")
    print ("Cheking 10S bar")
    if os.path.exists(tick_path) is False:
        print ("%s not found" % tick_path)
        print ("Building %s" % tick_path)
        os.makedirs(tick_path+name)
        ret = build_10s(path)
        #ret = ret.join(indics.build_indicators(ret['Close']))
        save_10s(tick_path+name+f, ret)
    else:
        if os.path.exists(tick_path + name + f) is False:
            print ("%s not found" % (tick_path + name))
            print ("Building %s" % tick_path + name)
            os.mkdir(tick_path+name)
            ret = build_10s(path)
            #ret = ret.join(indics.build_indicators(ret['Close']))
            save_10s(tick_path+name+f, ret)
        else:
            print ("%s found" % (tick_path+name))
            ret = load_10s(tick_path+name+f)
    return ret



def is_sort(data):
    for i in range(len(data) - 1):
        if data[i] > data[i + 1]:
            return False
    return True

def del_fail(data):
    a = 0
    time = []
    price = []
    i = 0
    while i < (len(data) - 1):
            a += 1
            l = 0
            if a == len(data['Time']) - 1:
                break
            if data['Time'][a] < data['Time'][i]:
                while data['Time'][a] < data['Time'][i] and a < len(data['Time']) - 1:
                    l += 1
                    a += 1
                i += l
            else:
                time.append(data['Time'][i])
                price.append(data['Price'][i])
            i += 1
    tmpp = pd.DataFrame(price, columns=['price'])
    tmpt = pd.DataFrame(time, columns=['time'])
    tmpt = tmpt.join(tmpp)
    print("Parsing accuracy :",(len(tmpt['price']) / len(data['Price'])) * 100,"%", "|", "Total number of valid tick in file :", len(tmpt['price'])-1)
    return tmpt

def tick_to_1m(data):
    opening = []
    opening.append(data['price'][0])
    close = []
    high = []
    low = []
    h = 0
    l = data['price'][0]
    for i in range(len(data['time']) - 1):
        if h < data['price'][i]:
            h = data['price'][i]
        if l > data['price'][i]:
            l = data['price'][i]
        if data['time'][i][4] < data['time'][i + 1][4]:
            close.append(data['price'][i])
            opening.append(data['price'][i + 1])
            high.append(h)
            low.append(l)
            h = 0
            l = data['price'][i + 1]
    low = pd.DataFrame(low, columns=['Low'])
    high = pd.DataFrame(high, columns=['High'])
    close = pd.DataFrame(close, columns=['Close'])
    opening = pd.DataFrame(opening, columns=['Open'])
    prices = opening.join(close)
    prices = prices.join(high)
    prices = prices.join(low)
    prices = prices.drop(len(prices) - 1)
    return prices

def auto_save(onem, tick, period, stock_name):
    while True:
        time.sleep(period)
        files = stock_name + time.strftime("_%d_%m_%y") + ".csv"
        onem.to_csv(files, mode='a')
        tick.to_csv(files, mode='a')

def get_data():
    files = ""
    return tick_to_1m(del_fail(open_row(files)))

############################

# prints formatted price
def formatPrice(n):
        return "{0:.2f}".format(n) + " €"

def EformatPrice(n):
        return "{0:.2f}".format(n) + " ISK"

# returns the vector containing stock data from a fixed file
def getStockDataVec(key):
        vec = []
        full = []
        path = "data/" + key + ".csv"
        #lines = open(path, "r").read().splitlines()
        #names = ['ID', 'Time', 'Open', 'High', 'Low', 'Close', 'RSI', 'Volatility']
        names = ['Time', 'Open', 'High', 'Low', 'Close', '']
        #names = ['ID', 'Close', 'RSI', 'MACD', 'Volatility', 'EMA20', 'EMA50', 'EMA100']
        #names = ['Time', 'BID', 'ASK', 'VOL']
        #names = ['Time', 'Price', 'Volume']
        row = pd.read_csv(path, names=names, header=0, sep=';')#, names = names)
        '''
        for line in lines[1:]:
            vec.append(float(line.split(";")[4]))

        '''
        time = row['Time'].copy(deep=True)
        vec = row['Close'].copy(deep=True)

        row.drop(row.columns[[0, 1, 2, 3, 5]], axis = 1, inplace = True)
        '''
        for l in range(len(row['ASK'])):
            vec.append(row['ASK'].iloc[l])

        row['EMA20'] /= 10000
        row['EMA50'] /= 10000
        row['EMA100'] /= 10000
        row['Close'] /= 10000
        row['RSI'] /= 100
        '''
        return vec, row, time

# returns the sigmoid
def sigmoid(x):
        return 1 / (1 + math.exp(-x))

# returns an an n-day state representation ending at time t
def getState(data, t, n):
        d = t - n + 1

        tmp = np.asarray(data)

        block = tmp[d:t + 1] if d >= 0 else np.concatenate([-d * [tmp[0]]] + [tmp[0:t + 1]])

        '''
        for i in range(len(block) - 1):
            tmp = []
            for r in block[i]:
                tmp.append(r)
            for z in inv_block[i]:
                tmp.append(z)
            res.append(np.asarray(tmp))
        res = np.asarray(res)
        '''
        res = []
        for i in range(n - 1):
            res.append(sigmoid(block[i + 1][0] - block[i][0]))#), block[i + 1][1], block[i + 1][2]])
        return np.array(res)

def act_processing(act):
    if act > 0:
        return ([1, 0, 0])
    elif act < 0:
        return ([0, 1, 0])
    else:
        return ([0, 0, 1])
