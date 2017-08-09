import numpy as np
import pandas as pd
import time

class environnement():

    def __init__(self):
        self.new_ticks = None
        self.new_1m = None
        self.path = "./dataset/"


    def set_1m(self, onem):
        self.new_1m = onem
        return self.new_1m

    def get_1m(self):
        return self.new_1m

    def set_ticks(self, ticks):
        self.new_ticks = ticks
        return self.new_ticks

    def get_ticks(self):
        return self.new_ticks



def moyenne(value, index, period):
    res = 0
    time = period
    if (len(value) - index < period):
        time = len(value) - index
    for i in range (time):
        res += value[i + index]
    if (time == 0):
        return value
    res/=time
    return (res)

def calc_MME(stock, period):
    result = []
    A = (2 / ( 1 + period ))
    for i in range (len(stock)):
        if (i + 1) < len(stock):
            result.append(moyenne(stock, i, period) * A + 
            moyenne(stock, i + 1, period) * (1 - A))
        else:
            result.append(moyenne(stock, i, period))
    return result

def src_hin_period(stock, period):
    h = 0
    for i in range (period):
        if (stock[i] > h):
            h = stock[i];
    return h

def src_lin_period(stock, period):
    l = 100
    for i in range (period):
        if (stock[i] < l):
            l = stock[i]
    return l

def src_close(stock, index):
    return stock[index]

def calc_D(K, period):
    result = []
    for i in range (len(K)):
        result.append(moyenne(K, i, period))
    return result

def calc_K(stock, period):
    result = []
    for i in range (len(stock)):
        result.append(100 * ((src_close(stock['Close'], i) -
        src_lin_period(stock['Low'], period)) /
        (src_hin_period(stock['High'], period) -
        src_lin_period(stock['Low'], period))))
    return result

def difference(A, B):
    result = []
    for i in range (len(A)):
        result.append(A[i] - B[i])
    return result

def calc_rsi(stock):
    res = []
    period = 14
    high = calc_MME(stock['High'], period)
    low = calc_MME(stock['Low'], period)
    for i in range (len(stock)):
        res.append( 100 * ( high[i] / ( high[i] + low[i] ) ) )
    return res

def calc_stochastique(stock):
    name = ['D', 'K']
    stoch = pd.DataFrame(columns=name)
    period = 14
    stoch['K'] = calc_K(stock, period)
    stoch['D'] = calc_D(stoch['K'], period)
    return difference(stoch['K'], stoch['D'])


def get_indicators(stock):
    name = ['MME20', 'MME50', 'MME100', 'Stoch', 'RSI']
    period = [20, 50, 100]
    indics = pd.DataFrame(columns=name)
    for i in range (len(name)):
        if (name[i] == 'Stoch'):
            indics[name[i]] = calc_stochastique(stock)
        elif (name[i] == 'RSI'):
            indics['RSI'] = calc_rsi(stock)
        else:
            indics[name[i]] = calc_MME(stock['Close'], period[i])
    return (indics)

def open_row(files, names):
    #files = "./dataset/"+"EUR_USD"+time.strftime("_%d_%m_%y")+".csv"
    print ("Opening :", files)
    csv = pd.read_csv(files, names=names, header = 0, error_bad_lines=False, sep=';')
    return csv

def is_sort(data):
    a = 0
    for i in range(len(data) - 1):
        a += 1
        if data[i] > data[a]:
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
    tmp = None
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
