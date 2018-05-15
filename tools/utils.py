import numpy as np
import pandas as pd

import time
import os
import math
from tqdm import tqdm
import subprocess

from .indicators import Indicators


def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def str2bool(value):
    if str(value).lower() in ("yes", "y", "true",  "t", "1", "1.0"): return True
    if str(value).lower() in ("no",  "n", "false", "f", "0", "0.0"): return False
    raise Exception('Invalid value for boolean conversion: ' + str(value))

############################

# prints formatted price
def formatPrice(n):
        return "{0:.2f}".format(n) + " €"

# returns the vector containing stock data from a fixed file
def getStockDataVec(key):
        path = "data/" + key + ".csv"
        if not os.path.exists(path):
            raise ValueError("Your stock {} isnt in data/ directory.".format(key))
        vec = None
        row = None
        chunksize = 10000
        nlines = subprocess.check_output('wc -l %s' % path, shell=True)
        nlines = int(nlines.split()[0])
        chunksize = nlines // 10
        lines = subprocess.check_output('head %s' % path, shell=True).decode()
        lines = lines.split('\n')[0]

        if ',' in lines:
            sep = ','
            len_row = len(lines.split(sep))
            if len_row == 4:
                names = ['Time', 'BID', 'ASK', 'VOL']
            elif len_row == 3:
                names = ['Time', 'Price', 'Volume']
        elif ';' in lines:
            sep = ';'
            len_row = len(lines.split(sep))
            if len_row == 6:
                names = ['Time', 'Open', 'High', 'Low', 'Close', '']

        for i in tqdm(range(0, nlines, chunksize), desc="Loading data "):
            df = pd.read_csv(path, header=None, sep=sep, nrows=chunksize, skiprows=i)#, names = names)
            df.columns = names
            if row is not None:
                row = row.append(df, ignore_index = True)
            else:
                row = df.copy(deep=True)

        time = row['Time'].copy(deep=True)

        if len_row == 4 and ',' in sep:
            vec = row['ASK'].copy(deep=True)
            row.drop(row.columns[[0, 1, 3]], axis=1, inplace=True)

        elif len_row == 3 and ',' in sep:
            vec = row['Price'].copy(deep=True)
            #row.drop(row.columns[[0, 2]], axis=1, inplace=True)

        elif len_row == 6 and ';' in sep:
            vec = row['Close'].copy(deep=True)
            row.drop(row.columns[[0, 1, 2, 3, 5]], axis=1, inplace=True)

        return vec, row, time

# returns the sigmoid
def sigmoid(x):
        return 1 / (1 + math.exp(-x))

# returns an an n-day state representation ending at time t
def getState(data, t, n):
        d = t - n + 1
        tmp = np.asarray(data)
        block = tmp[d:t + 1] if d >= 0 else np.concatenate([-d * [tmp[0]]] + [tmp[0:t + 1]])
        res = []
        for i in range(n - 1):
            res.append(sigmoid(block[i + 1] - block[i]))
        return np.array(res)

def act_processing(act):
    if act == 1:
        return ([1, 0, 0])
    elif act == 2:
        return ([0, 1, 0])
    else:
        return ([0, 0, 1])
