import numpy as np
import pandas as pd
import time
import os

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

##### Indicators #####

def moyenne(value, index, period):
    res = 0
    time = period
    if (index - time < 1):
        time = index
    if (time == 0):
        return value[time]
    res = sum(value[index - time : index])
    res /= time
    return (res)

def calc_MME(stock, period):
    result = []
    A = (2 / ( 1 + period ))
    for i in range (len(stock)):
        if i > 0:
            result.append(moyenne(stock, i, period) * A + moyenne(stock, i - 1, period) * (1 - A))
        else:
            result.append(moyenne(stock, i, period))
    return result

# Search High in period

def src_hin_period(stock, period, index):
    h = 0
    if index - period < 1:
        index = 0
    else:
        index = index - period + 1
    if index == 0:
        return stock[index]
    while index <= period:
        if (stock[index] > h):
            h = stock[index]
        index += 1
    return h

# Search low in period

def src_lin_period(stock, period, index):
    l = 100000
    if index - period < 1:
        index = 0
    else:
        index = index - period + 1
    if index == 0:
        return stock[index]
    while index <= period:
        if (stock[index] < l):
            l = stock[index]
        index += 1
    return l

# Search close with start index

def src_close(stock, index):
    return stock[index]

# Calc stochastique

## Calc %D of stoch

def calc_D(K, period):
    result = []
    for i in range (len(K)):
        result.append(moyenne(K, i, period))
    return result

## Calc %K of stoch

def calc_K(stock, period):
    result = []
    for i in range (len(stock)):
        result.append(100 * ((src_close(stock['Close'], i) - src_lin_period(stock['Low'], period, i)) / (src_hin_period(stock['High'], period, i) - src_lin_period(stock['Low'], period, i))))
    return result

def difference(A, B):
    return A - B

def hmvt_avg(stock, period, index):
    h = 0
    i = 0
    last = 0
    z = 0
    if index - period < 1:
        index = 0
    else:
        index = index - period
    if index == 0:
        return stock[index]
    while index < period:
        if z > 0:
            last = stock[index - 1]
        z = 1
        if (stock[index] > last):
            h += stock[index]
            i += 1
        index += 1
    if i == 0:
        return h
    h /= i
    return h

def lmvt_avg(stock, period, index):
    l = 0
    i = 0
    last = l
    z = 0
    if index - period < 1:
        index = 0
    else:
        index = index - period
    if index == 0:
        return stock[index]
    while index < period:
        if z > 0:
            last = stock[index - 1]
        z = 1
        if (stock[index] < last):
            l += stock[index]
            i += 1
        index += 1
    if i == 0:
        return l
    l /= i
    return l

# Calc RSI

def calc_rsi(stock):
    res = []
    period = 14
    for i in range (len(stock)):
        res.append(100 - ( 100 / (hmvt_avg(stock['Open'], period, i) + lmvt_avg(stock['Open'], period, i))))
    return res

def calc_stochastique(stock):
    name = ['D', 'K']
    stoch = pd.DataFrame(columns=name)
    period = 14
    stoch['K'] = calc_K(stock, period)
    stoch['D'] = calc_D(stoch['K'], period)
    return difference(stoch['K'], stoch['D'])


# Indicators managment

## Indicators builder

def build_indics(stock, name):
    period = [20, 50, 100]
    indics = pd.DataFrame(columns = name)
    for i in range (len(name)):
        if (name[i] == 'Stoch'):
            print ('Building %s' % (name[i]))
            indics[name[i]] = calc_stochastique(stock)
        elif (name[i] == 'RSI'):
            print ('Building %s' % (name[i]))
            indics[name[i]] = calc_rsi(stock)
        else:
            print ('Building %s' % (name[i]))
            indics[name[i]] = calc_MME(stock['Open'], period[i])
    return indics

def save_indics(path, indics):
    indics.to_csv(path, sep = ';', mode = 'w')
    print ("Indicators saved in %s" % path)

def load_indics(files):
    names = ['ID' ,'MME20', 'MME50', 'MME100']
    indics = pd.read_csv(files, names=names, header = 0, error_bad_lines=False, sep=';')
    indics.drop(indics.columns[[0]], axis = 1, inplace = True)
    print ("Indicators loaded from %s" % files)
    return indics

## Check if Indicators are already builded and build if needed

def check_indics(data_name, stock):
    path = "./indicators"
    name = ['MME20', 'MME50', 'MME100']
    indics_path = path + "/" + data_name
    print ("Cheking indicators")
    if os.path.exists(path) is False:
        print ("%s not founded" % indics_path)
        print ("Building %s" % indics_path)
        os.makedirs(indics_path)
        indics = build_indics(stock, name)
        save_indics(indics_path+"/indics", indics)
    else:
        if os.path.exists(indics_path + "/indics") is False:
            print ("%s not founded" % (indics_path + "/indics"))
            if os.path.exists(indics_path) is False:
                print ("Building %s" % indics_path)
                os.mkdir(indics_path)
            indics = build_indics(stock, name)
            save_indics(indics_path+"/indics", indics)
        else:
            print ("%s founded" % indics_path)
            indics = load_indics(indics_path+"/indics")
    return indics

####################

#### Data managment ####

# Getting data

def open_row(files, names, d):
    #files = "./dataset/"+"EUR_USD"+time.strftime("_%d_%m_%y")+".csv"
    print ("Opening : %s" % files)
    csv = pd.read_csv(files, names=names, header = 0, error_bad_lines=False, sep=';')
    csv.drop(csv.columns[[0, 5]], axis = 1, inplace = True)
    indics = check_indics(d, csv)
    indics['MME20'] /= 10000
    indics['MME50'] /= 10000
    indics['MME100'] /= 10000
    csv = csv.join(indics)
    return csv

# Get all data

def get_all_data(path, names):
    # list path directoy
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
                csv.drop(csv.columns[[0, 5]], axis = 1, inplace = True)
                indics = check_indics(d, csv)
                indics['MME20'] /= 10000
                indics['MME50'] /= 10000
                indics['MME100'] /= 10000
                csv = csv.join(indics)
                if data is None:
                    data = csv
                else:
                    data = data.append(csv, ignore_index=True)
    print ("All files opened")
    return data

# Change tick to 10s

def build_10s():


def save_10s(stock, path):
    stock.to_csv(path, sep = ';', mode = 'w')
    print ("Data saved in %s" % path)

def load_10s(path):
    names = []
    stock = pd.read_csv(path, names=names, header = 0, error_bad_lines=False, sep=';')
    print ("Data loaded from %s" % path)
    return stock

def check_10s():



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

############################
